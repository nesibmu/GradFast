import { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router";
import { Send, Sun, Moon, ChevronDown, ChevronUp, Lock, Shuffle, CheckCircle, RefreshCw } from "lucide-react";
import {
  generatePlan, getAdvisorResponse, applyMove, regeneratePlan,
  PlanData, TermData, getTermUnits, validateTermUnits, countTotalUnits
} from "../api";

interface Message { role: "user" | "assistant"; content: string; }

export function Planner() {
  const location = useLocation();
  const navigate = useNavigate();
  const answers = (location.state as any)?.answers ?? {};

  const [plan, setPlan] = useState<PlanData | null>(null);
  const [terms, setTerms] = useState<TermData[]>([]);
  const [loading, setLoading] = useState(true);
  const [restructuring, setRestructuring] = useState(false);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [thinking, setThinking] = useState(false);
  const [openAltId, setOpenAltId] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const isDark = localStorage.getItem("theme") === "dark";
  const toggleTheme = () => { localStorage.setItem("theme", isDark ? "light" : "dark"); window.location.reload(); };

  useEffect(() => { if (!answers.name) { navigate("/questions"); return; } loadPlan(); }, []);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const loadPlan = async () => {
    try {
      setLoading(true);
      setError("");
      const data = await generatePlan(
        answers.name ?? "", answers.university ?? "", answers.major ?? "",
        answers.year ?? "", answers.targetGrad ?? "", answers.credits ?? ""
      );
      setPlan(data);
      setTerms(data.terms);
      const total = countTotalUnits(data.terms);
      setMessages([{
        role: "assistant",
        content: `Here is ${answers.name}'s plan — ${data.terms.length} quarters, ${total} units, graduating ${data.expectedGraduation}. Red = locked requirement, yellow = flexible (click to see alternatives including transfer options). Ask me anything.`
      }]);
    } catch (e: any) {
      setError(e.message ?? "Failed to generate plan");
    } finally {
      setLoading(false);
    }
  };

  const doRestructure = async (newGradDate: string) => {
    if (!plan) return;
    setRestructuring(true);
    try {
      const newPlan = await regeneratePlan(plan, newGradDate, terms);
      setPlan(newPlan);
      setTerms(newPlan.terms);
      const total = countTotalUnits(newPlan.terms);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: `Plan rebuilt for ${newPlan.expectedGraduation}. ${newPlan.terms.length} quarters, ${total} units. Scroll up to review.`
      }]);
    } catch (e: any) {
      setMessages(prev => [...prev, { role: "assistant", content: `Rebuild failed: ${e.message}` }]);
    } finally {
      setRestructuring(false);
    }
  };

  const handleSend = async () => {
    const msg = inputMessage.trim();
    if (!msg || thinking || !plan) return;
    setInputMessage("");
    const newMsgs: Message[] = [...messages, { role: "user", content: msg }];
    setMessages(newMsgs);
    setThinking(true);
    try {
      const response = await getAdvisorResponse(
        newMsgs.map(m => ({ role: m.role, content: m.content })),
        plan, terms
      );
      const { action, courseCode, toTerm, newGradDate } = response.planAction;

      if (action === "move" && courseCode && toTerm) {
        const updated = applyMove(terms, courseCode, toTerm);
        if (updated) setTerms(updated);
      }

      // Detect restructure — from LLM signal OR from user message directly
      const lower = msg.toLowerCase();
      const gradMatch = lower.match(/(spring|winter|fall|summer)\s+20\d\d/i);
      const isExplicitChange = gradMatch && (
        lower.includes("change") || lower.includes("instead") || lower.includes("graduate by") ||
        lower.includes("graduation to") || lower.includes("fix") || lower.includes("rebuild") ||
        lower.includes("restructure") || lower.includes("make") || lower.includes("want") ||
        lower.includes("switch") || lower.includes("i actually want")
      );
      const resolvedGradDate = newGradDate || (isExplicitChange && gradMatch
        ? gradMatch[0].replace(/(^|\s)\S/g, s => s.toUpperCase()) : null);

      setMessages([...newMsgs, { role: "assistant", content: response.message }]);

      if ((action === "restructure" || isExplicitChange) && resolvedGradDate) {
        setThinking(false);
        doRestructure(resolvedGradDate);
        return;
      }
    } catch (e: any) {
      setMessages([...newMsgs, { role: "assistant", content: `Error: ${e?.message ?? "something went wrong"}. Check your API key.` }]);
    } finally {
      setThinking(false);
    }
  };

  // ── Loading screens ───────────────────────────────────────────────────────

  if (loading || restructuring) return (
    <div className="h-screen bg-background flex flex-col items-center justify-center gap-5">
      <div className="relative w-12 h-12">
        <div className="w-12 h-12 border-2 border-primary/20 rounded-full" />
        <div className="w-12 h-12 border-2 border-primary border-t-transparent rounded-full animate-spin absolute inset-0" />
      </div>
      <p style={{ fontSize: "var(--text-xl)" }} className="text-foreground font-semibold">
        {restructuring ? `Rebuilding ${answers.name}'s plan...` : `Building ${answers.name}'s plan...`}
      </p>
    </div>
  );

  if (error) return (
    <div className="h-screen bg-background flex flex-col items-center justify-center gap-4 px-6 text-center">
      <p style={{ fontSize: "var(--text-xl)" }} className="text-foreground font-semibold">Something went wrong</p>
      <p style={{ fontSize: "var(--text-sm)" }} className="text-muted-foreground max-w-md">{error}</p>
      <p style={{ fontSize: "var(--text-sm)" }} className="text-muted-foreground max-w-md">Make sure VITE_OPENROUTER_API_KEY is set in your .env file.</p>
      <button onClick={loadPlan} className="mt-2 px-5 py-2.5 bg-primary text-primary-foreground rounded-xl text-sm font-medium hover:opacity-90">Try again</button>
    </div>
  );

  const totalUnits = countTotalUnits(terms);

  return (
    <div className="h-screen bg-background flex flex-col overflow-hidden">

      {/* Header */}
      <div className="border-b border-border/40 px-6 py-3 bg-background/95 backdrop-blur-sm z-20 flex-shrink-0 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span style={{ fontSize: "var(--text-xl)" }} className="font-bold text-foreground tracking-tight">GradFast</span>
          {plan && <span style={{ fontSize: "var(--text-sm)" }} className="text-muted-foreground">{plan.university} · {plan.major}</span>}
        </div>
        <div className="flex items-center gap-4">
          {plan && <span style={{ fontSize: "var(--text-sm)" }} className="text-muted-foreground">Graduating: <span className="text-foreground font-medium">{plan.expectedGraduation}</span></span>}
          <button onClick={() => navigate("/questions")} className="px-3 py-1.5 rounded-lg bg-card border border-border/40 hover:bg-accent transition-all text-xs text-muted-foreground flex items-center gap-1.5">
            <RefreshCw className="w-3 h-3" /> Start Over
          </button>
          <button onClick={toggleTheme} className="p-2 rounded-lg bg-card border border-border/40 hover:bg-accent transition-all">
            {isDark ? <Sun className="w-4 h-4 text-foreground" /> : <Moon className="w-4 h-4 text-foreground" />}
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 flex overflow-hidden min-h-0">

        {/* Calendar */}
        <div className="flex-1 flex flex-col overflow-hidden min-w-0">
          {/* Legend */}
          <div className="flex-shrink-0 px-6 py-2 border-b border-border/20 bg-background flex items-center gap-5 flex-wrap">
            {[["bg-red-400/40","Hard requirement"],["bg-amber-400/70","Flexible — click for alternatives"],["bg-emerald-400/70","Completed / transferable"]].map(([c,l]) => (
              <div key={l} className="flex items-center gap-1.5">
                <div className={`w-2.5 h-2.5 rounded-sm ${c}`} />
                <span style={{ fontSize: "var(--text-xs)" }} className="text-muted-foreground">{l}</span>
              </div>
            ))}
            <span style={{ fontSize: "var(--text-xs)" }} className={`ml-auto font-semibold ${totalUnits >= 180 ? "text-emerald-400" : "text-amber-400"}`}>
              {totalUnits} / 180 units {totalUnits >= 180 ? "✓ Graduation requirement met" : `— need ${180 - totalUnits} more`}
            </span>
          </div>

          {/* Terms */}
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-2">
            {terms.map((term) => {
              const u = getTermUnits(term);
              const uc = validateTermUnits(u);
              return (
                <div key={term.id} className="border border-border/30 rounded-xl overflow-hidden bg-card/40">
                  <button onClick={() => setTerms(prev => prev.map(t => t.id === term.id ? { ...t, expanded: !t.expanded } : t))}
                    className="w-full px-5 py-3 flex items-center justify-between hover:bg-accent/20 transition-colors group">
                    <div className="flex items-center gap-3">
                      <span style={{ fontSize: "var(--text-sm)" }} className="font-semibold text-foreground group-hover:text-primary transition-colors">{term.name} {term.year}</span>
                      <span style={{ fontSize: "var(--text-xs)" }} className={`px-2.5 py-0.5 rounded-full ${uc.status === "error" ? "bg-red-400/20 text-red-400" : uc.status === "warning" ? "bg-amber-400/20 text-amber-400" : "text-muted-foreground bg-secondary/60"}`}>{uc.message}</span>
                    </div>
                    {term.expanded ? <ChevronUp className="w-3.5 h-3.5 text-muted-foreground" /> : <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />}
                  </button>

                  {term.expanded && (
                    <div className="px-5 pb-4 space-y-1.5">
                      {(term.courses || []).map((course) => {
                        const isOpen = openAltId === course.id;
                        const hasAlts = course.type === "flexible" && (course.alternatives?.length ?? 0) > 0;
                        const bg = course.type === "hard" ? "border-l-2 border-l-red-400/40 bg-red-400/[0.05]"
                          : course.type === "flexible" ? "border-l-2 border-l-amber-400/55 bg-amber-400/[0.05]"
                          : "border-l-2 border-l-emerald-400/55 bg-emerald-400/[0.05]";
                        return (
                          <div key={course.id}>
                            <div className={`rounded-lg px-4 py-2.5 transition-all ${bg} ${hasAlts ? "cursor-pointer" : ""}`}
                              onClick={() => hasAlts && setOpenAltId(isOpen ? null : course.id)}>
                              <div className="flex items-center justify-between gap-3">
                                <div className="flex items-center gap-2 flex-1 min-w-0">
                                  {course.type === "hard" && <Lock className="w-3 h-3 text-red-400/55 flex-shrink-0" />}
                                  {course.type === "flexible" && <Shuffle className="w-3 h-3 text-amber-400/65 flex-shrink-0" />}
                                  {course.type === "completed" && <CheckCircle className="w-3 h-3 text-emerald-400/65 flex-shrink-0" />}
                                  <span style={{ fontSize: "var(--text-sm)" }} className="font-bold text-primary flex-shrink-0">{course.code}</span>
                                  <span style={{ fontSize: "var(--text-sm)" }} className="text-foreground/90 truncate">{course.name}</span>
                                  <span style={{ fontSize: "var(--text-xs)" }} className="text-muted-foreground/50 truncate hidden lg:block">· {course.requirement}</span>
                                </div>
                                <div className="flex items-center gap-1.5 flex-shrink-0">
                                  <span style={{ fontSize: "var(--text-xs)" }} className="text-muted-foreground bg-background/30 px-2 py-0.5 rounded-full">{course.credits}u</span>
                                  {hasAlts && <ChevronDown className={`w-3 h-3 text-amber-400/60 transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`} />}
                                </div>
                              </div>
                              {course.notes && <p style={{ fontSize: "var(--text-xs)" }} className="text-muted-foreground/40 italic mt-1 ml-5">{course.notes}</p>}
                            </div>
                            {hasAlts && isOpen && (
                              <div className="ml-5 mt-1 pl-3 border-l border-amber-400/20 space-y-1 pb-1">
                                <p style={{ fontSize: "var(--text-xs)" }} className="text-amber-400/60 font-semibold uppercase tracking-wide py-1">Alternatives for {course.code}</p>
                                {course.alternatives!.map((alt, i) => (
                                  <div key={i} className="px-3 py-2 bg-amber-400/[0.04] border border-amber-400/10 rounded-lg">
                                    <p style={{ fontSize: "var(--text-xs)" }} className="text-foreground/75 leading-relaxed">{alt}</p>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}

            {/* Info panels */}
            {plan && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2 pb-4">
                {[
                  { title: "Key Policies", items: plan.keyPolicies ?? [] },
                  { title: "Loopholes & Tips", items: plan.loopholes ?? [] },
                  { title: "Transfer & Double-Count", items: [
                    ...(plan.transferOptions ?? []).map(t => `${t.requirement} → ${t.transferCourse} (${t.notes})`),
                    ...(plan.doubleCountingOpportunities ?? [])
                  ]}
                ].map(({ title, items }) => (
                  <div key={title} className="bg-card/40 border border-border/25 rounded-xl p-4">
                    <h3 style={{ fontSize: "var(--text-xs)" }} className="font-bold text-primary/70 uppercase tracking-wider mb-2.5">{title}</h3>
                    <ul className="space-y-2">
                      {(items ?? []).map((item, i) => (
                        <li key={i} style={{ fontSize: "var(--text-xs)" }} className="text-muted-foreground leading-relaxed border-b border-border/10 pb-1.5 last:border-0 last:pb-0">{item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chat */}
        <div className="w-[360px] flex-shrink-0 border-l border-border/30 flex flex-col bg-card/30">
          <div className="px-5 py-3.5 border-b border-border/25 flex-shrink-0">
            <p style={{ fontSize: "var(--text-xs)" }} className="text-muted-foreground font-semibold uppercase tracking-widest">Your Advisor</p>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[94%] rounded-2xl px-4 py-2.5 ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-secondary/40 text-foreground border border-border/20"}`}>
                  <p style={{ fontSize: "var(--text-sm)" }} className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {thinking && (
              <div className="flex justify-start">
                <div className="bg-secondary/40 border border-border/20 rounded-2xl px-4 py-3">
                  <div className="flex gap-1 items-center">
                    {[0,150,300].map(d => <div key={d} className="w-1.5 h-1.5 bg-muted-foreground/50 rounded-full animate-bounce" style={{ animationDelay: `${d}ms` }} />)}
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {messages.length <= 1 && (
            <div className="px-4 pb-3 flex-shrink-0 space-y-1.5">
              <p style={{ fontSize: "var(--text-xs)" }} className="text-muted-foreground uppercase tracking-wider px-0.5 mb-2">Try asking</p>
              {[
                "What are my WAYS requirements and which double-count with CS?",
                "Move CS106B to Spring 2027",
                "Can I graduate by Spring 2028?",
                "What if I study abroad Winter of my junior year?",
                "I want to transfer PWR1 — what are my options?",
                "Change my graduation to Spring 2028",
              ].map(s => (
                <button key={s} onClick={() => setInputMessage(s)} style={{ fontSize: "var(--text-xs)" }}
                  className="w-full text-left px-3 py-2 bg-background/20 hover:bg-accent/50 border border-border/20 rounded-xl text-muted-foreground hover:text-foreground transition-all">
                  {s}
                </button>
              ))}
            </div>
          )}

          <div className="border-t border-border/25 p-4 flex-shrink-0">
            <div className="flex gap-2">
              <input type="text" value={inputMessage}
                onChange={e => setInputMessage(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                placeholder="Ask anything about your plan..."
                style={{ fontSize: "var(--text-sm)" }}
                className="flex-1 bg-background/30 border border-border/30 rounded-xl px-3.5 py-2.5 text-foreground placeholder:text-muted-foreground outline-none focus:border-primary transition-colors"
                disabled={thinking} />
              <button onClick={handleSend} disabled={!inputMessage.trim() || thinking}
                className="bg-primary text-primary-foreground p-2.5 rounded-xl hover:opacity-90 transition-all disabled:opacity-30 disabled:cursor-not-allowed flex-shrink-0">
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
