import { useNavigate } from "react-router";
import { ArrowRight, Sun, Moon } from "lucide-react";

export function Landing() {
  const navigate = useNavigate();

  const isDark = document.documentElement.classList.contains('dark') ||
                 localStorage.getItem('theme') === 'dark';

  const toggleTheme = () => {
    const newTheme = isDark ? 'light' : 'dark';
    localStorage.setItem('theme', newTheme);
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6 relative overflow-hidden">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/10 pointer-events-none" />

      {/* Theme toggle */}
      <button
        onClick={toggleTheme}
        className="absolute top-8 right-8 p-3 rounded-xl bg-card hover:bg-accent transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 z-10 border border-border/50"
        style={{ transform: 'translateZ(0)' }}
        aria-label="Toggle theme"
      >
        {isDark ? (
          <Sun className="w-5 h-5 text-foreground" />
        ) : (
          <Moon className="w-5 h-5 text-foreground" />
        )}
      </button>

      <div className="max-w-4xl mx-auto text-center space-y-12 relative z-10">
        <div className="space-y-6">
          <h1
            style={{
              fontSize: 'var(--text-6xl)',
              textShadow: isDark
                ? '0 4px 20px rgba(255, 255, 255, 0.1)'
                : '0 4px 20px rgba(0, 0, 0, 0.05)'
            }}
            className="tracking-tight text-foreground leading-tight transform hover:scale-[1.02] transition-transform duration-300"
          >
            Graduate faster than they think you can.
          </h1>
          <p style={{ fontSize: 'var(--text-xl)' }} className="text-muted-foreground max-w-2xl mx-auto">
            Smart degree planning powered by AI. Map your path to graduation with precision.
          </p>
        </div>

        <button
          onClick={() => navigate("/questions")}
          className="group inline-flex items-center gap-2 bg-primary text-primary-foreground px-10 py-5 rounded-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1"
          style={{
            boxShadow: isDark
              ? '0 10px 40px rgba(255, 255, 255, 0.2), 0 4px 12px rgba(255, 255, 255, 0.1)'
              : '0 10px 40px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.1)'
          }}
        >
          Get Started
          <ArrowRight className="w-5 h-5 group-hover:translate-x-2 transition-transform duration-300" />
        </button>
      </div>
    </div>
  );
}
