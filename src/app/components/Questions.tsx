import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router";
import { ArrowRight, Sun, Moon, Search } from "lucide-react";

const UNIVERSITIES = [
  "American University","Arizona State University","Auburn University",
  "Barnard College","Bates College","Boston College","Boston University",
  "Bowdoin College","Brandeis University","Brown University","Bryn Mawr College",
  "Bucknell University","Caltech","Carleton College","Carnegie Mellon University",
  "Case Western Reserve University","Claremont McKenna College","Clark University",
  "Colby College","Colgate University","Colorado School of Mines","Columbia University",
  "Cornell University","Dartmouth College","Davidson College","De Anza College",
  "Denison University","DePaul University","DePauw University","Dickinson College",
  "Drake University","Drexel University","Duke University","Elon University",
  "Emory University","Florida A&M University","Florida State University",
  "Fordham University","Furman University","George Mason University",
  "George Washington University","Georgetown University","Georgia Tech",
  "Gettysburg College","Gonzaga University","Grinnell College","Hamilton College",
  "Hampton University","Harvard University","Harvey Mudd College",
  "Haverford College","Hobart and William Smith Colleges","Howard University",
  "Illinois Institute of Technology","Indiana University","Iowa State University",
  "Johns Hopkins University","Kenyon College","Knox College","Lafayette College",
  "Lawrence University","Lehigh University","Loyola Marymount University",
  "Loyola University Chicago","Macalester College","Marquette University",
  "Miami University","Michigan State University","Middlebury College",
  "MIT","Morehouse College","Mount Holyoke College","Muhlenberg College",
  "New York University (NYU)","Northeastern University","Northwestern University",
  "Oberlin College","Ohio State University","Penn State University",
  "Pepperdine University","Pomona College","Princeton University","Purdue University",
  "RPI (Rensselaer Polytechnic Institute)","Reed College","Rice University",
  "Rutgers University","Santa Clara University","Scripps College",
  "Seattle University","Skidmore College","Smith College","Spelman College",
  "St. Lawrence University","Stanford University","Stevens Institute of Technology",
  "Swarthmore College","Syracuse University","Temple University","Tufts University",
  "Tulane University","UC Berkeley","UC Davis","UC Irvine","UC Los Angeles (UCLA)",
  "UC Merced","UC Riverside","UC San Diego","UC Santa Barbara","UC Santa Cruz",
  "UNC Chapel Hill","Union College","University of Arizona",
  "University of Chicago","University of Colorado Boulder",
  "University of Connecticut","University of Delaware","University of Florida",
  "University of Georgia","University of Illinois Urbana-Champaign",
  "University of Iowa","University of Kansas","University of Kentucky",
  "University of Maryland","University of Massachusetts Amherst",
  "University of Miami","University of Michigan","University of Minnesota",
  "University of North Carolina","University of Notre Dame","University of Oregon",
  "University of Pennsylvania","University of Pittsburgh","University of Richmond",
  "University of Rochester","University of San Francisco","University of South Carolina",
  "University of Southern California (USC)","University of Texas at Austin",
  "University of Utah","University of Virginia","University of Washington",
  "University of Wisconsin-Madison","Vanderbilt University","Vassar College",
  "Villanova University","Virginia Tech","Wake Forest University",
  "Washington University in St. Louis","Wellesley College","Wesleyan University",
  "Williams College","Worcester Polytechnic Institute (WPI)","Xavier University",
  "Yale University","Other",
];

const MAJORS = [
  // Computer Science & Technology
  "Artificial Intelligence","Computer Engineering","Computer Science",
  "Computer Science & Economics","Computer Science & Mathematics",
  "Computer Science & Statistics","Cybersecurity","Data Science",
  "Human-Computer Interaction","Information Science","Information Systems",
  "Software Engineering",
  // Engineering
  "Aerospace Engineering","Biomedical Engineering","Chemical Engineering",
  "Civil Engineering","Electrical Engineering","Environmental Engineering",
  "Industrial Engineering","Materials Science & Engineering",
  "Mechanical Engineering","Nuclear Engineering","Systems Engineering",
  // Math & Sciences
  "Applied Mathematics","Astronomy","Biochemistry","Biology","Biophysics",
  "Chemistry","Cognitive Science","Environmental Science","Geology",
  "Mathematics","Neuroscience","Physics","Statistics",
  // Business & Economics
  "Accounting","Business Administration","Economics","Finance",
  "Management","Management Information Systems","Marketing",
  "Operations Research","Supply Chain Management",
  // Social Sciences
  "Anthropology","Communication Studies","Criminal Justice",
  "Gender Studies","Geography","History","International Relations",
  "Journalism","Linguistics","Philosophy","Political Science",
  "Psychology","Public Policy","Religious Studies","Sociology","Urban Studies",
  // Arts & Humanities
  "Architecture","Art History","Classics","Comparative Literature",
  "Creative Writing","Design","English","Ethnic Studies","Film Studies",
  "Music","Studio Art","Theater",
  // Health
  "Kinesiology","Nursing","Nutrition","Pharmacy","Pre-Dentistry",
  "Pre-Medicine","Public Health",
  "Other",
].filter(Boolean);

interface SearchDropdownProps {
  onSelect: (val: string) => void;
  options: string[];
  placeholder: string;
  isLast: boolean;
}

function SearchDropdown({ onSelect, options, placeholder, isLast }: SearchDropdownProps) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const filtered = query.length === 0
    ? options
    : options.filter(o => o.toLowerCase().includes(query.toLowerCase()));

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const pick = (opt: string) => {
    setQuery(opt);
    setSelected(opt);
    setOpen(false);
  };

  return (
    <div ref={ref} className="relative w-full">
      <div className="relative">
        <Search className="absolute left-0 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground/40 pointer-events-none" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={e => { setQuery(e.target.value); setSelected(""); setOpen(true); }}
          onFocus={() => setOpen(true)}
          onKeyDown={e => {
            if (e.key === "Enter" && filtered.length > 0) { pick(filtered[0]); }
            if (e.key === "Escape") setOpen(false);
          }}
          placeholder={placeholder}
          style={{ fontSize: "var(--text-2xl)" }}
          className="w-full bg-transparent border-b-2 border-border focus:border-primary outline-none pb-4 pl-8 text-foreground placeholder:text-muted-foreground/40 transition-all duration-300"
          autoComplete="off"
          spellCheck={false}
        />
      </div>

      {open && filtered.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-3 bg-card border border-border/60 rounded-2xl shadow-2xl z-50 overflow-hidden max-h-60 overflow-y-auto">
          {filtered.slice(0, 50).map(opt => (
            <button
              key={opt}
              onMouseDown={e => { e.preventDefault(); pick(opt); }}
              style={{ fontSize: "var(--text-base)" }}
              className="w-full text-left px-5 py-3 text-foreground hover:bg-accent transition-colors border-b border-border/20 last:border-0"
            >
              {opt}
            </button>
          ))}
          {filtered.length > 50 && (
            <div style={{ fontSize: "var(--text-sm)" }} className="px-5 py-3 text-muted-foreground text-center">
              {filtered.length - 50} more results — keep typing
            </div>
          )}
        </div>
      )}

      {(selected || query.trim()) && (
        <button
          onClick={() => {
            const val = selected || query.trim();
            if (val) onSelect(val);
          }}
          style={{ fontSize: "var(--text-base)" }}
          className="mt-6 inline-flex items-center gap-2 text-primary hover:text-primary/80 transition-all duration-300 hover:gap-3"
        >
          {isLast ? "Build my plan" : "Next"}
          <ArrowRight className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}

interface Question {
  id: string;
  question: string;
  placeholder: string;
  type: "text" | "select" | "searchdrop";
  options?: string[];
}

const QUESTIONS: Question[] = [
  { id: "name", question: "What's your name?", placeholder: "e.g. Alex", type: "text" },
  { id: "university", question: "Which university do you attend?", placeholder: "Search universities...", type: "searchdrop", options: UNIVERSITIES },
  { id: "major", question: "What's your major?", placeholder: "e.g. Computer Science, Economics, Biology...", type: "text" },
  { id: "year", question: "What year are you currently in?", placeholder: "", type: "select",
    options: ["Incoming freshman","Freshman","Sophomore","Junior","Senior"] },
  { id: "targetGrad", question: "When do you want to graduate?", placeholder: "e.g. Spring 2028 or June 2028", type: "text" },
  { id: "credits", question: "Any AP, IB, or transfer credits? List them, or skip.", placeholder: "e.g. AP Calc BC (5), AP CS A (5), IB Chemistry HL (7)", type: "text" },
];

export function Questions() {
  const navigate = useNavigate();
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [inputValue, setInputValue] = useState("");

  const isDark = document.documentElement.classList.contains("dark") || localStorage.getItem("theme") === "dark";
  const toggleTheme = () => { localStorage.setItem("theme", isDark ? "light" : "dark"); window.location.reload(); };

  const q = QUESTIONS[currentQ];
  const isLast = currentQ === QUESTIONS.length - 1;
  const progress = (currentQ / QUESTIONS.length) * 100;

  const advance = (val: string) => {
    if (!val.trim() && q.id !== "credits") return;
    const newAnswers = { ...answers, [q.id]: val };
    setAnswers(newAnswers);
    setInputValue("");
    if (isLast) {
      navigate("/planner", { state: { answers: newAnswers } });
    } else {
      setCurrentQ(currentQ + 1);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/10 pointer-events-none" />

      <button onClick={toggleTheme}
        className="absolute top-8 right-8 p-3 rounded-xl bg-card hover:bg-accent transition-all duration-300 shadow-lg hover:scale-105 z-10 border border-border/50"
        aria-label="Toggle theme">
        {isDark ? <Sun className="w-5 h-5 text-foreground" /> : <Moon className="w-5 h-5 text-foreground" />}
      </button>

      <div className="w-full h-1 bg-secondary flex-shrink-0">
        <div className="h-full bg-primary transition-all duration-500" style={{ width: `${progress}%` }} />
      </div>

      <div className="flex-1 flex items-center justify-center px-6 relative z-10">
        <div className="max-w-2xl w-full space-y-10">

          <div className="space-y-4">
            <div style={{ fontSize: "var(--text-sm)" }} className="text-muted-foreground font-medium tracking-wide">
              {currentQ + 1} / {QUESTIONS.length}
            </div>
            <h1
              style={{ fontSize: "var(--text-5xl)", textShadow: isDark ? "0 4px 20px rgba(255,255,255,0.1)" : "0 4px 20px rgba(0,0,0,0.05)" }}
              className="tracking-tight text-foreground leading-tight font-bold"
            >
              {q.question}
            </h1>
          </div>

          <div className="space-y-4">
            {q.type === "searchdrop" ? (
              <SearchDropdown
                key={q.id}
                onSelect={advance}
                options={q.options!}
                placeholder={q.placeholder}
                isLast={isLast}
              />
            ) : q.type === "select" ? (
              <div className="space-y-3">
                {q.options!.map((opt, i) => (
                  <button key={opt} onClick={() => advance(opt)}
                    style={{ fontSize: "var(--text-base)", animationDelay: `${i * 40}ms` }}
                    className="w-full text-left px-6 py-4 bg-card border border-border hover:border-primary text-foreground rounded-xl transition-all duration-200 hover:shadow-xl hover:scale-[1.01]">
                    {opt}
                  </button>
                ))}
              </div>
            ) : (
              <>
                <input
                  type="text"
                  value={inputValue}
                  onChange={e => setInputValue(e.target.value)}
                  onKeyDown={e => { if (e.key === "Enter") advance(inputValue); }}
                  placeholder={q.placeholder}
                  style={{ fontSize: "var(--text-2xl)" }}
                  className="w-full bg-transparent border-b-2 border-border focus:border-primary outline-none pb-4 text-foreground placeholder:text-muted-foreground/40 transition-all duration-300"
                  autoFocus
                  autoComplete="off"
                />
                <div className="flex items-center gap-6 pt-2">
                  <button onClick={() => advance(inputValue)}
                    disabled={!inputValue.trim() && q.id !== "credits"}
                    style={{ fontSize: "var(--text-base)" }}
                    className="inline-flex items-center gap-2 text-primary hover:text-primary/80 transition-all duration-300 disabled:opacity-30 disabled:cursor-not-allowed hover:gap-3">
                    {isLast ? "Build my plan" : "Next"}
                    <ArrowRight className="w-5 h-5" />
                  </button>
                  {q.id === "credits" && (
                    <button onClick={() => advance("")}
                      style={{ fontSize: "var(--text-base)" }}
                      className="text-muted-foreground hover:text-foreground transition-colors">
                      Skip
                    </button>
                  )}
                </div>
              </>
            )}
          </div>

          {currentQ > 0 && (
            <button
              onClick={() => { setCurrentQ(currentQ - 1); setInputValue(answers[QUESTIONS[currentQ - 1].id] ?? ""); }}
              style={{ fontSize: "var(--text-sm)" }}
              className="text-muted-foreground hover:text-foreground transition-colors">
              ← Back
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
