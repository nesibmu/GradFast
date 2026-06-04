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

// What the LLM returns for a plan update
export interface PlanAction {
  // "move": move courseCode from sourceTerm to destTerm (swap displaced course back)
  // "none": no change
  action: "move" | "none";
  courseCode?: string;      // e.g. "CS106B"
  fromTerm?: string;        // e.g. "Winter 2026"  (name + year)
  toTerm?: string;          // e.g. "Spring 2026"
  message: string;          // plain text, no markdown
}

export interface AdvisorResponse {
  message: string;
  planAction: PlanAction;
}

// ── Plan generation ──────────────────────────────────────────────────────────

export async function generatePlan(
  name: string, university: string, major: string,
  year: string, targetGrad: string, credits: string
): Promise<PlanData> {
  const startYear = 2025;

  const prompt = `Generate a COMPLETE graduation plan for this student. Include every single quarter — no partial plans.

Student:
- Name: ${name}
- University: ${university}
- Major: ${major}
- Current year: ${year} (starting Fall ${startYear})
- Target graduation: ${targetGrad || "Spring " + (startYear + 4)}
- Prior credits: ${credits || "None"}

CRITICAL RULES:
- Use REAL course codes for ${university} ONLY. Do NOT use Stanford course codes unless the university is Stanford.
- American University uses AU Core (AUCORE) requirements. MIT uses GIRs. UC Berkeley uses breadth requirements. Each school is different.
- Look up the correct total units for ${university} ${major} — it varies by school (120-180 units typically)
- Use the correct academic calendar: quarters (Fall/Winter/Spring) or semesters (Fall/Spring) for ${university}
- Incoming freshman needs a complete plan: typically 12 quarters or 8 semesters
- Every term: 3-5 courses, 12-18 units (quarters) or 15-18 credits (semesters)
- Hard requirements: empty alternatives array.
- Flexible requirements: 3+ real alternatives. Each alternative must include course code, full name, units, and when offered.
- WAYS requirements: NEVER label as just "Humanities" or "GER". Always use the specific WAYS area name (WAYS-AII, WAYS-AQR, WAYS-CE, WAYS-ED, WAYS-ER, WAYS-FR, WAYS-SI, WAYS-SMA). Every WAYS course must be type "flexible" with 3+ real alternatives.
- Stanford has exactly 8 WAYS requirements. Spread them across years. Each is ~4 units.
- Do not invent vague requirements like "Humanities Requirement" — use the real Stanford terminology.
- Return ONLY valid JSON, no markdown, no prose

{
  "studentName": "${name}",
  "university": "${university}",
  "major": "${major}",
  "totalUnitsRequired": 180,
  "unitsPerQuarter": 16,
  "expectedGraduation": "${targetGrad || "Spring " + (startYear + 4)}",
  "keyPolicies": ["<real policy 1>","<real policy 2>","<real policy 3>"],
  "loopholes": ["<specific loophole with petition name>","<another>","<another>"],
  "transferOptions": [{"requirement":"<code — name>","transferCourse":"<real accepted course>","notes":"<specific details>"}],
  "doubleCountingOpportunities": ["<specific course that satisfies two requirements>"],
  "terms": [
    {
      "id": "fall-${startYear}",
      "name": "Fall",
      "year": "${startYear}",
      "expanded": true,
      "courses": [
        {
          "id": "c1",
          "code": "CS106A",
          "name": "Programming Methodology",
          "credits": 5,
          "type": "hard",
          "requirement": "CS Core — Programming Foundation (required before CS106B, CS107)",
          "alternatives": [],
          "notes": "Must complete before CS106B. Offered every quarter."
        },
        {
          "id": "c2",
          "code": "MATH51",
          "name": "Linear Algebra, Multivariable Calculus",
          "credits": 5,
          "type": "hard",
          "requirement": "Mathematics Foundation — required for CS103, CS109, CS161",
          "alternatives": [],
          "notes": "Core math prerequisite for most upper-division CS."
        },
        {
          "id": "c3",
          "code": "PWR1",
          "name": "Writing and Rhetoric 1",
          "credits": 4,
          "type": "flexible",
          "requirement": "Communication Requirement A — must complete by end of sophomore year",
          "alternatives": [
            "Foothill College ENGL 1A (4u) — Stanford has accepted this for PWR1 credit via transfer petition. Take over summer before freshman year.",
            "De Anza ENGL 1A (5u) — accepted for Communication Req A by Stanford registrar. Cheaper option.",
            "PWR1CE (4u) — Community-engaged section of PWR1, same requirement, different focus. Offered Fall/Winter/Spring."
          ],
          "notes": "Some students petition to waive with a strong AP English score (5) or transfer credit."
        },
        {
          "id": "c4",
          "code": "WAYS-AII",
          "name": "Aesthetic and Interpretive Inquiry",
          "credits": 4,
          "type": "flexible",
          "requirement": "WAYS GER — Aesthetic and Interpretive Inquiry (one of 8 WAYS areas required)",
          "alternatives": [
            "MUSIC101 — Listening to Music (4u) — fulfills WAYS AII, offered every quarter, no prerequisites",
            "ARTHIST1 — Art and Architecture (4u) — fulfills WAYS AII, offered Fall/Spring",
            "FILMSTD1 — Introduction to Film (4u) — fulfills WAYS AII, popular with CS students, offered Fall/Winter",
            "TAPS101 — Theater and Performance (4u) — fulfills WAYS AII, offered Fall/Spring"
          ],
          "notes": "Any WAYS AII approved course works. Check ExploreCourses for current offerings."
        }
      ]
    }
  ]
}

Continue terms through ALL quarters until ${targetGrad || "Spring " + (startYear + 4)}. Total units across all terms must equal 180.`;

  const resp = await fetch(BASE_URL, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({
      model: MODEL,
      messages: [
        { role: "system", content: `You are an expert academic planner with deep knowledge of every US university. CRITICAL: You must use the EXACT course codes, course names, unit counts, and graduation requirements for the SPECIFIC university in the prompt — NOT Stanford unless Stanford is specified. Every university has different requirements: American University uses AU Core requirements, MIT uses GIRs, UC Berkeley uses breadth requirements. Use the correct system for the correct school. Return ONLY valid JSON. No markdown. No prose.` },
        { role: "user", content: prompt },
      ],
      temperature: 0.1,
      max_tokens: 8000,
    }),
  });

  if (!resp.ok) throw new Error(`API error ${resp.status}: ${await resp.text()}`);
  const data = await resp.json();
  let raw = data.choices[0].message.content.trim();
  if (raw.startsWith("```")) raw = raw.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "");
  return JSON.parse(raw) as PlanData;
}

// ── Advisor chat ─────────────────────────────────────────────────────────────

const ADVISOR_SYSTEM = `You are an expert academic advisor who actually does the work. You never say "consult your advisor" — YOU are the advisor. You have deep knowledge of Stanford's programs, course catalog, transfer policies, and study abroad options.

RULES — follow exactly:
1. Plain text only. No markdown, no hashtags (#), no asterisks (*), no dashes as bullets. Use numbers (1. 2. 3.) for lists.
2. Be SPECIFIC and THOROUGH. Look at the student's actual schedule and give real concrete answers.
3. Never deflect. Never say "consult your advisor." YOU are the advisor. Give the actual answer.
4. Use real course codes from the student's plan.
5. For moves: set action to "move", fill courseCode and toTerm exactly.
6. toTerm must be exactly "Season YYYY" e.g. "Winter 2026"

UNIT WARNINGS — check every time you move a course:
- Stanford maximum is 20 units per quarter without a petition. If a move pushes a quarter over 20 units, warn the student: "This puts [term] at [X] units. Stanford caps at 20 — you would need to petition for an overload, which requires advisor approval and is typically approved for students in good standing. You can petition at axess.stanford.edu."
- Stanford minimum is 12 units per quarter for full-time status. If removing a course drops a quarter below 12 units, warn the student: "This leaves [term] at only [X] units, below Stanford's 12-unit minimum. You need to move another course in, or you risk losing full-time status which affects financial aid and visa status for international students."
- Always state unit counts after a move: "After this move: [source term] has [X] units, [dest term] has [Y] units."

WAYS REQUIREMENTS — Stanford has exactly 8 WAYS areas, never call them just "Humanities":
- WAYS-AII: Aesthetic and Interpretive Inquiry (e.g. MUSIC101, ARTHIST1, FILMSTD1, TAPS101)
- WAYS-AQR: Applied Quantitative Reasoning (e.g. STATS60, MS&E120, ECON50)
- WAYS-CE: Creative Expression (e.g. MUSIC19, ARTSTUDI1, TAPS20)
- WAYS-ED: Engaging Diversity (e.g. AMSTUD1, FEMGEN1, CSRE1)
- WAYS-ER: Ethical Reasoning (e.g. PHIL1, ETHICSOC1, POLISCI1)
- WAYS-FR: Formal Reasoning (e.g. PHIL151, LINGUIST130, CS103 — CS103 satisfies both WAYS-FR and CS Core)
- WAYS-SI: Social Inquiry (e.g. ECON1, POLISCI1, PSYCH1)
- WAYS-SMA: Scientific Method and Analysis (e.g. PHYSICS41, BIO1, CHEM31A)
- Always name the specific WAYS area. Never say "Humanities Requirement" or "GER".
- CS103 satisfies WAYS-FR and CS Core simultaneously — always mention this double-count opportunity.

FULL PLAN RESTRUCTURE — when the student asks to graduate earlier or later, or says "move everything" or "restructure my plan":
- Set action to "restructure" in your response
- In your message, tell the student exactly which quarters get compressed, which courses move where, and what the new unit counts per quarter would be
- Be specific: name every course that moves and where it goes
- Warn about any quarter that would exceed 20 units
- Warn about prerequisites that would be violated
- End with: "To apply this restructure, I recommend regenerating your plan with Spring 2028 as your target graduation. Click Start Over and re-enter your info with the new graduation date for a clean updated plan."

Return ONLY this JSON:
{
  "action": "move | none",
  "courseCode": "<exact course code or null>",
  "fromTerm": "<Season YYYY or null>",
  "toTerm": "<Season YYYY or null>",
  "message": "<thorough plain text answer, 4-10 sentences, no markdown, specific to their actual schedule>"
}`;

export async function getAdvisorResponse(
  messages: Array<{ role: string; content: string }>,
  plan: PlanData,
  currentTerms: TermData[]
): Promise<AdvisorResponse> {
  const planSummary = currentTerms.map(t =>
    `${t.name} ${t.year}: ${t.courses.map(c => `${c.code}(${c.credits}u)`).join(", ")}`
  ).join("\n");

  const system = `${ADVISOR_SYSTEM}

Current plan — ${plan.studentName} at ${plan.university}, ${plan.major}, graduating ${plan.expectedGraduation}:
${planSummary}`;

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
      max_tokens: 1000,
    }),
  });

  if (!resp.ok) throw new Error(`API error ${resp.status}`);
  const data = await resp.json();
  let raw = data.choices[0].message.content.trim();
  if (raw.startsWith("```")) raw = raw.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "");

  let planAction: PlanAction = { action: "none", message: "" };
  let message = "";

  try {
    const parsed = JSON.parse(raw);
    message = parsed.message ?? raw;
    planAction = {
      action: parsed.action ?? "none",
      courseCode: parsed.courseCode ?? undefined,
      fromTerm: parsed.fromTerm ?? undefined,
      toTerm: parsed.toTerm ?? undefined,
      message: parsed.message ?? "",
    };
  } catch {
    // If JSON parse fails, treat as plain message
    message = raw.replace(/#{1,6}\s/g, "").replace(/\*\*/g, "").replace(/\*/g, "").replace(/`/g, "").trim();
  }

  // Strip any stray markdown from message
  message = message
    .replace(/#{1,6}\s/g, "")
    .replace(/\*\*/g, "")
    .replace(/\*/g, "")
    .replace(/`/g, "")
    .trim();

  return { message, planAction };
}

// ── Frontend course move logic ───────────────────────────────────────────────
// This runs in the browser — doesn't depend on the LLM returning valid terms.
// It finds the course by code, removes it from its current term, adds it to the target term.

export function applyMove(
  terms: TermData[],
  courseCode: string,
  toTermLabel: string  // e.g. "Spring 2026"
): TermData[] | null {
  const code = courseCode.toUpperCase().trim();
  const target = toTermLabel.trim().toLowerCase();

  // Find the course
  let foundCourse: CourseData | null = null;
  let fromTermId: string | null = null;

  for (const term of terms) {
    const match = term.courses.find(c => c.code.toUpperCase() === code);
    if (match) {
      foundCourse = match;
      fromTermId = term.id;
      break;
    }
  }

  if (!foundCourse || !fromTermId) return null;

  // Find the destination term
  const destTerm = terms.find(t =>
    `${t.name} ${t.year}`.toLowerCase() === target ||
    t.name.toLowerCase() === target.split(" ")[0]?.toLowerCase() && t.year === target.split(" ")[1]
  );

  if (!destTerm) return null;
  if (destTerm.id === fromTermId) return null; // already there

  // Build updated terms
  return terms.map(term => {
    if (term.id === fromTermId) {
      return { ...term, courses: term.courses.filter(c => c.code.toUpperCase() !== code) };
    }
    if (term.id === destTerm.id) {
      return { ...term, expanded: true, courses: [...term.courses, foundCourse!] };
    }
    return term;
  });
}
