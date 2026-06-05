const OPENROUTER_API_KEY = import.meta.env.VITE_OPENROUTER_API_KEY || "";
const BASE_URL = "https://openrouter.ai/api/v1/chat/completions";
const MODEL = "openai/gpt-4o-mini";

const HEADERS = {
  "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
  "Content-Type": "application/json",
  "HTTP-Referer": "https://gradfast.app",
  "X-Title": "GradFast",
};

export interface CourseData {
  id: string;
  code: string;
  name: string;
  credits: number;
  type: "hard" | "flexible" | "completed";
  requirement: string;
  alternatives?: string[];
  notes?: string;
}

export interface TermData {
  id: string;
  name: string;
  year: string;
  courses: CourseData[];
  expanded: boolean;
}

export interface PlanData {
  studentName: string;
  university: string;
  major: string;
  totalUnitsRequired: number;
  unitsPerQuarter: number;
  expectedGraduation: string;
  keyPolicies: string[];
  loopholes: string[];
  transferOptions: Array<{ requirement: string; transferCourse: string; notes: string }>;
  doubleCountingOpportunities: string[];
  terms: TermData[];
}

export interface PlanAction {
  action: "move" | "none" | "restructure";
  courseCode?: string;
  fromTerm?: string;
  toTerm?: string;
  newGradDate?: string;
  message: string;
}

export interface AdvisorResponse {
  message: string;
  planAction: PlanAction;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function normalizeTerms(terms: TermData[]): TermData[] {
  return (terms || []).map((t, ti) => ({
    ...t,
    courses: (t.courses || []).map((c, ci) => ({
      ...c,
      credits: Number(c.credits) || 0,
      id: c.id || `c-${ti}-${ci}`,
      alternatives: c.alternatives || [],
    })),
  }));
}

export function getTermUnits(term: TermData): number {
  return (term.courses || []).reduce((s, c) => s + (Number(c.credits) || 0), 0);
}

export function validateTermUnits(units: number): { status: "ok" | "warning" | "error"; message: string } {
  if (units < 12) return { status: "error", message: `${units}u — below 12 minimum` };
  if (units > 22) return { status: "error", message: `${units}u — exceeds 22 max` };
  if (units > 20) return { status: "warning", message: `${units}u — petition required` };
  return { status: "ok", message: `${units}u` };
}

export function countTotalUnits(terms: TermData[]): number {
  return (terms || []).reduce((s, t) => s + getTermUnits(t), 0);
}

function padToMinUnits(terms: TermData[], minUnits: number): TermData[] {
  let total = countTotalUnits(terms);
  if (total >= minUnits) return terms;

  const electives = [
    { code: "CS147", name: "Intro to HCI Design", credits: 4, req: "CS Elective — HCI depth track" },
    { code: "CS221", name: "AI: Principles and Techniques", credits: 4, req: "CS Elective — AI depth track" },
    { code: "MUSIC101", name: "Listening to Music", credits: 4, req: "WAYS-AII elective" },
    { code: "PSYCH1", name: "Introduction to Psychology", credits: 4, req: "WAYS-SI elective" },
    { code: "PHIL1", name: "Introduction to Philosophy", credits: 4, req: "WAYS-ER elective" },
    { code: "CS152", name: "Trust and Safety Engineering", credits: 3, req: "CS Elective" },
    { code: "CS193P", name: "iOS App Development", credits: 3, req: "CS Elective" },
    { code: "ENGR40M", name: "An Intro to Making: EE", credits: 4, req: "CS/WAYS-SMA Elective" },
    { code: "STATS110", name: "Statistical Methods in Engineering", credits: 3, req: "Stats elective" },
    { code: "INTLPOL201", name: "International Relations", credits: 4, req: "WAYS-SI elective" },
    { code: "CS248", name: "Interactive Computer Graphics", credits: 4, req: "CS Elective" },
    { code: "CS255", name: "Introduction to Cryptography", credits: 3, req: "CS Elective" },
    { code: "ECON1", name: "Principles of Economics", credits: 5, req: "WAYS-SI elective" },
    { code: "THINK51", name: "Critical Thinking", credits: 4, req: "WAYS-ER elective" },
  ];

  const updated = terms.map(t => ({ ...t, courses: [...t.courses] }));
  let ei = 0;

  for (let i = updated.length - 1; i >= 0 && total < minUnits; i--) {
    // re-check live unit count each iteration
    while (getTermUnits(updated[i]) < 20 && total < minUnits) {
      const el = electives[ei % electives.length];
      ei++;
      updated[i].courses.push({
        id: `pad-${i}-${ei}`,
        code: el.code,
        name: el.name,
        credits: el.credits,
        type: "flexible",
        requirement: el.req,
        alternatives: [],
        notes: "Added to reach 180 unit minimum. Can be swapped for any elective you prefer.",
      });
      total += el.credits;
    }
  }
  return updated;
}

// ── Plan generation ───────────────────────────────────────────────────────────

export async function generatePlan(
  name: string, university: string, major: string,
  year: string, targetGrad: string, credits: string
): Promise<PlanData> {

  const startYear = 2026; // current entering class
  const gradMatch = (targetGrad || "").match(/(\d{4})/);
  const gradYear = gradMatch ? parseInt(gradMatch[1]) : startYear + 4;
  const gradSeason = (targetGrad || "Spring").toLowerCase().includes("winter") ? "Winter"
    : (targetGrad || "").toLowerCase().includes("fall") ? "Fall" : "Spring";

  let numQuarters = (gradYear - startYear) * 3;
  if (gradSeason === "Winter") numQuarters -= 2;
  else if (gradSeason === "Spring") numQuarters -= 1;
  numQuarters = Math.max(9, Math.min(numQuarters, 16));

  const targetUPQ = Math.max(15, Math.ceil(180 / numQuarters));
  const hasAPCalcBC = /calc\s*bc|calculus\s*bc/i.test(credits);
  const hasAPCSA = /cs\s*a\b|computer\s*science\s*a/i.test(credits);
  const gradTarget = targetGrad || `Spring ${startYear + 4}`;

  // Build a compact but complete prompt — avoid token overload
  const prompt = `Generate a COMPLETE Stanford ${major} graduation plan as JSON only.

STUDENT: ${name}, entering Fall ${startYear}, target graduation ${gradTarget}
AP Calc BC: ${hasAPCalcBC ? "YES → place into MATH51 Fall ${startYear}" : "NO → sequence: MATH19→MATH20→MATH21→MATH51"}
AP CS A: ${hasAPCSA ? "YES → start at CS106B" : "NO → start at CS106A"}
Prior credits: ${credits || "none"}

PREREQ RULES (never violate):
CS106A → CS106B → CS107 → CS110 → CS111
CS106B → CS103 → CS109 → CS161
MATH19→20→21→MATH51 (unless AP Calc BC) → CS109 needs MATH51
PWR1 before PWR2, PWR1 must finish by end of Year 2

UNIT RULES:
- ${numQuarters} quarters available (Fall ${startYear} through ${gradTarget})
- MUST total 180+ units across all quarters
- Each quarter: 12–20 units (aim for ${targetUPQ}u)
- Quarters over 20u are allowed but mark them with petition note

REQUIRED COURSES:
Hard core: CS106A(5u), CS106B(5u), CS107(5u), CS110(4u), CS111(4u), CS103(5u), CS109(5u), CS161(5u)
Math: MATH19(3u), MATH20(3u), MATH21(3u), MATH51(5u) [skip MATH19-21 if AP Calc BC]
Writing: PWR1(4u), PWR2(4u)
WAYS (all 8, 4u each = 32u): WAYS-AII, WAYS-AQR, WAYS-CE, WAYS-ED, WAYS-ER, WAYS-FR(=CS103), WAYS-SI, WAYS-SMA
CS Electives: at least 5 upper-div CS courses (3-5u each)
General electives: fill remaining units to reach 180+

CS103 counts for BOTH "CS Core" AND "WAYS-FR" — include once, mark type "hard", requirement "CS Core + WAYS-FR"

RETURN ONLY this JSON structure, nothing else:
{
  "studentName": "${name}",
  "university": "${university || "Stanford University"}",
  "major": "${major}",
  "totalUnitsRequired": 180,
  "unitsPerQuarter": ${targetUPQ},
  "expectedGraduation": "${gradTarget}",
  "keyPolicies": ["180 units to graduate","12u min per quarter","20u max without petition","PWR1 by end of Year 2"],
  "loopholes": ["CS103 satisfies CS Core + WAYS-FR simultaneously","AP Calc BC skips MATH19-21 (saves 9u)","AP CS A skips CS106A (saves 5u)","PWR1 via Foothill ENGL 1A ~$150 vs on-campus"],
  "transferOptions": [{"requirement":"PWR1","transferCourse":"Foothill ENGL 1A (4u)","notes":"Grade B+ required, petition axess.stanford.edu"}],
  "doubleCountingOpportunities": ["CS103 = CS Core + WAYS-FR","PHYSICS41 = science req + WAYS-SMA"],
  "terms": [
    {"id":"fall-${startYear}","name":"Fall","year":"${startYear}","expanded":true,"courses":[
      {"id":"c-0-0","code":"${hasAPCSA ? "CS106B" : "CS106A"}","name":"${hasAPCSA ? "Programming Abstractions" : "Programming Methodology"}","credits":5,"type":"hard","requirement":"CS Core","alternatives":[],"notes":"${hasAPCSA ? "Placed in via AP CS A" : "First CS course — no prereqs"}"},
      {"id":"c-0-1","code":"${hasAPCalcBC ? "MATH51" : "MATH19"}","name":"${hasAPCalcBC ? "Linear Algebra & Multivariable Calculus" : "Calculus I"}","credits":${hasAPCalcBC ? 5 : 3},"type":"hard","requirement":"Math Core","alternatives":[],"notes":"${hasAPCalcBC ? "Placed in via AP Calc BC" : "Start of calc sequence"}"},
      {"id":"c-0-2","code":"PWR1","name":"Writing and Rhetoric 1","credits":4,"type":"flexible","requirement":"Communication Req A","alternatives":["Foothill ENGL 1A (4u, ~$150, grade B+ required)","De Anza ENGL 1A (5u, pre-approved)"],"notes":"Must complete by end of Year 2"},
      {"id":"c-0-3","code":"MUSIC101","name":"Listening to Music","credits":4,"type":"flexible","requirement":"WAYS-AII","alternatives":["ARTHIST1 (4u)","FILMSTD1 (4u)","TAPS101 (4u)"],"notes":"Any WAYS-AII course works"}
    ]}
  ]
}

NOW add all remaining terms through ${gradTarget}. Every term must have 12-20 units. Total across all terms must be 180+. Include every required course listed above. Add CS electives and general electives to fill remaining units.`;

  const resp = await fetch(BASE_URL, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({
      model: MODEL,
      messages: [
        { role: "system", content: "You are a Stanford academic planner. Return ONLY valid JSON — no markdown, no explanation, no text outside the JSON object. Total units must be 180+. Never violate prerequisite order." },
        { role: "user", content: prompt },
      ],
      temperature: 0.1,
      max_tokens: 10000,
    }),
  });

  if (!resp.ok) throw new Error(`API error ${resp.status}: ${await resp.text()}`);
  const data = await resp.json();
  let raw = data.choices[0].message.content.trim();
  if (raw.startsWith("```")) raw = raw.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "");

  // Repair truncated JSON
  if (!raw.endsWith("}")) {
    const lb = raw.lastIndexOf("}");
    if (lb > 0) raw = raw.substring(0, lb + 1);
    const opens = (raw.match(/\[/g) || []).length - (raw.match(/\]/g) || []).length;
    const oopens = (raw.match(/\{/g) || []).length - (raw.match(/\}/g) || []).length;
    for (let i = 0; i < opens; i++) raw += "]";
    for (let i = 0; i < oopens; i++) raw += "}";
  }

  let parsed: PlanData;
  try { parsed = JSON.parse(raw) as PlanData; }
  catch { throw new Error("Plan generation failed — AI returned invalid JSON. Please try again."); }

  parsed.terms = normalizeTerms(parsed.terms);
  parsed.totalUnitsRequired = 180;
  parsed.keyPolicies = parsed.keyPolicies || [];
  parsed.loopholes = parsed.loopholes || [];
  parsed.transferOptions = parsed.transferOptions || [];
  parsed.doubleCountingOpportunities = parsed.doubleCountingOpportunities || [];

  // Guarantee 180 units
  if (countTotalUnits(parsed.terms) < 180) {
    parsed.terms = padToMinUnits(parsed.terms, 180);
  }

  return parsed;
}

// ── Regenerate (just re-run generatePlan with new grad date) ──────────────────

export async function regeneratePlan(
  currentPlan: PlanData,
  newGradDate: string,
  _currentTerms: TermData[]
): Promise<PlanData> {
  return generatePlan(
    currentPlan.studentName,
    currentPlan.university,
    currentPlan.major,
    "Sophomore",
    newGradDate,
    ""
  );
}

// ── Advisor ───────────────────────────────────────────────────────────────────
// NOTE: Keep system prompt SHORT to avoid token limit errors.
// Transfer DB and prereq chain are summarized, not fully inlined.

export async function getAdvisorResponse(
  messages: Array<{ role: string; content: string }>,
  plan: PlanData,
  currentTerms: TermData[]
): Promise<AdvisorResponse> {
  const totalUnits = countTotalUnits(currentTerms);

  // Compact plan summary — just term + units + course codes
  const planSummary = currentTerms.map(t => {
    const u = getTermUnits(t);
    return `${t.name} ${t.year}(${u}u): ${t.courses.map(c => c.code).join(", ")}`;
  }).join("\n");

  const system = `You are GradFast, a Stanford academic advisor. Give specific, useful answers. Never just say "see your advisor" — give a real answer first, then suggest confirming if needed.

STUDENT PLAN — ${plan.studentName}, ${plan.major}, graduating ${plan.expectedGraduation}
Units: ${totalUnits}/180 ${totalUnits < 180 ? `(SHORT by ${180 - totalUnits})` : "(OK)"}
${planSummary}

STANFORD RULES:
- 180 units to graduate
- 12u min per quarter (full-time status), 20u max without petition (21-22u needs advisor petition at axess.stanford.edu)
- Prereqs: CS106A→CS106B→CS107→CS110→CS111; CS106B→CS103→CS109→CS161; MATH19→20→21→MATH51 (unless AP Calc BC); CS103+MATH51 both needed before CS109
- CS103 satisfies CS Core AND WAYS-FR simultaneously
- All 8 WAYS required: AII, AQR, CE, ED, ER, FR(=CS103), SI, SMA
- PWR1 transfer options: Foothill ENGL 1A (4u, ~$150, grade B+), De Anza ENGL 1A (5u), AP Eng Lang score 5 = waiver. Petition at axess.stanford.edu.
- Study abroad: Stanford-in-Oxford/Berlin/Kyoto/Florence/Cape Town all give direct Stanford credit. CIEE/IES need petition.

RESPONSE — return ONLY this JSON, no other text:
{
  "action": "none | move | restructure",
  "courseCode": null,
  "fromTerm": null,
  "toTerm": null,
  "newGradDate": null,
  "message": "your plain text answer here — no markdown, no asterisks, use 1. 2. 3. for lists"
}

RULES:
- "move": set courseCode, fromTerm ("Season YYYY"), toTerm ("Season YYYY"). Check prereqs and unit counts. State new unit totals after move.
- "restructure": ONLY when student explicitly says to change graduation date (not just asks about it). Set newGradDate.
- "none": everything else — give a thorough specific answer in message.
- If asked "can I graduate earlier" → action "none", analyze their specific schedule, end with "say 'change my graduation to Spring 2028' to rebuild the plan."
- For course moves that push a quarter over 20u: explain petition process. For moves below 12u: warn about full-time status.`;

  const resp = await fetch(BASE_URL, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({
      model: MODEL,
      messages: [
        { role: "system", content: system },
        ...messages,
      ],
      temperature: 0.3,
      max_tokens: 800,
    }),
  });

  if (!resp.ok) {
    const errText = await resp.text();
    throw new Error(`API ${resp.status}: ${errText}`);
  }

  const data = await resp.json();
  let raw = data.choices[0].message.content.trim();
  if (raw.startsWith("```")) raw = raw.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "");

  let planAction: PlanAction = { action: "none", message: "" };
  let message = "";

  try {
    const parsed = JSON.parse(raw);
    message = (parsed.message ?? raw)
      .replace(/#{1,6}\s/g, "").replace(/\*\*/g, "").replace(/\*/g, "").replace(/`/g, "").trim();
    planAction = {
      action: parsed.action ?? "none",
      courseCode: parsed.courseCode ?? undefined,
      fromTerm: parsed.fromTerm ?? undefined,
      toTerm: parsed.toTerm ?? undefined,
      newGradDate: parsed.newGradDate ?? undefined,
      message,
    };
  } catch {
    message = raw.replace(/#{1,6}\s/g, "").replace(/\*\*/g, "").replace(/\*/g, "").replace(/`/g, "").trim();
  }

  return { message, planAction };
}

// ── Course move ───────────────────────────────────────────────────────────────

export function applyMove(
  terms: TermData[], courseCode: string, toTermLabel: string
): TermData[] | null {
  const code = courseCode.toUpperCase().trim();
  const target = toTermLabel.trim().toLowerCase();

  let found: CourseData | null = null;
  let fromId: string | null = null;

  for (const t of terms) {
    const m = t.courses.find(c => c.code.toUpperCase() === code);
    if (m) { found = m; fromId = t.id; break; }
  }
  if (!found || !fromId) return null;

  const dest = terms.find(t =>
    `${t.name} ${t.year}`.toLowerCase() === target ||
    (t.name.toLowerCase() === target.split(" ")[0]?.toLowerCase() && t.year === target.split(" ")[1])
  );
  if (!dest || dest.id === fromId) return null;

  return terms.map(t => {
    if (t.id === fromId) return { ...t, courses: t.courses.filter(c => c.code.toUpperCase() !== code) };
    if (t.id === dest.id) return { ...t, expanded: true, courses: [...t.courses, found!] };
    return t;
  });
}
