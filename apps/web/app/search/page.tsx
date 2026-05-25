"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  SlidersHorizontal, 
  Search, 
  User, 
  MapPin, 
  Briefcase, 
  Star, 
  Loader2,
  Sparkles,
  Menu,
  Home,
  FileText,
  Settings,
  BarChart3,
  MessageSquare,
  MoreVertical,
  X,
  Filter,
  ChevronDown,
  TrendingUp,
  Target,
  Zap,
  ArrowUpRight
} from "lucide-react";
import { searchApi } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";

export default function SearchPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [filters, setFilters] = useState({
    skills: "",
    location: "",
    limit: 10,
  });
  const [showFilters, setShowFilters] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/sign-in");
    }
  }, [authLoading, user, router]);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await searchApi.candidates({
        query,
        skills: filters.skills ? filters.skills.split(",").map((s) => s.trim()) : undefined,
        location: filters.location || undefined,
        limit: filters.limit,
      });
      setResults(data as any[]);
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const sidebarItems = [
    { icon: Home, label: "Dashboard", href: "/dashboard", active: false },
    { icon: User, label: "Candidates", href: "/candidates", active: false },
    { icon: Briefcase, label: "Jobs", href: "/jobs", active: false },
    { icon: FileText, label: "Resumes", href: "/resumes", active: false },
    { icon: Search, label: "Search", href: "/search", active: true },
    { icon: MessageSquare, label: "AI Copilot", href: "/copilot", active: false },
    { icon: BarChart3, label: "Analytics", href: "/analytics", active: false },
    { icon: Settings, label: "Settings", href: "/settings", active: false },
  ];

  const suggestedQueries = [
    "Find senior Python developers with Docker experience",
    "Machine learning engineers with NLP skills",
    "Full stack developers in San Francisco",
    "React developers with TypeScript experience",
  ];

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="h-12 w-12 rounded-full border-4 border-accent border-t-transparent"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Sidebar */}
      <motion.div
        initial={{ x: -300 }}
        animate={{ x: sidebarOpen ? 0 : -300 }}
        className="fixed left-0 top-0 z-50 h-full w-72 bg-background-card border-r border-background-border lg:static lg:translate-x-0"
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between p-6 border-b border-background-border">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-accent flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div>
                <div className="font-bold text-lg">Resume AI</div>
                <div className="text-xs text-foreground-muted">Intelligent Hiring</div>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-foreground-muted hover:text-foreground"
            >
              <MoreVertical className="h-5 w-5" />
            </button>
          </div>

          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-1">
              {sidebarItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 rounded-lg px-4 py-3 transition-colors ${
                      item.active
                        ? "bg-accent/10 text-foreground border border-accent/30"
                        : "text-foreground-muted hover:bg-background-elevated hover:text-foreground"
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </nav>

          <div className="p-4 border-t border-background-border">
            <div className="flex items-center gap-3 rounded-lg bg-background-elevated p-3">
              <div className="h-10 w-10 rounded-full bg-accent/20" />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm truncate">{user?.email || "User"}</div>
                <div className="text-xs text-foreground-muted">Recruiter</div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
        />
      )}

      <div className="lg:pl-72">
        <header className="sticky top-0 z-30 border-b border-background-border bg-background/80 backdrop-blur-xl">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-foreground-muted hover:text-foreground"
              >
                <Menu className="h-6 w-6" />
              </button>
              <div>
                <h1 className="text-2xl font-bold">Semantic Search</h1>
                <p className="text-sm text-foreground-muted">AI-powered candidate discovery</p>
              </div>
            </div>
          </div>
        </header>

        <main className="p-6">
          <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
            {/* Filters Sidebar */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="rounded-xl bg-background-card border border-background-border p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2 font-semibold">
                  <Filter className="h-5 w-5 text-accent" />
                  Filters
                </div>
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="text-sm text-foreground-muted hover:text-foreground transition-colors"
                >
                  {showFilters ? <X className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </button>
              </div>

              <AnimatePresence>
                {showFilters && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="space-y-6"
                  >
                    <div>
                      <label className="block text-sm text-foreground-muted mb-2">Skills</label>
                      <input
                        value={filters.skills}
                        onChange={(e) => setFilters({ ...filters, skills: e.target.value })}
                        placeholder="python, react, docker"
                        className="w-full rounded-lg bg-background-elevated border border-background-border px-4 py-3 text-sm text-foreground placeholder-foreground-subtle focus:outline-none focus:border-accent/50 transition-colors"
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-foreground-muted mb-2">Location</label>
                      <input
                        value={filters.location}
                        onChange={(e) => setFilters({ ...filters, location: e.target.value })}
                        placeholder="San Francisco, CA"
                        className="w-full rounded-lg bg-background-elevated border border-background-border px-4 py-3 text-sm text-foreground placeholder-foreground-subtle focus:outline-none focus:border-accent/50 transition-colors"
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-foreground-muted mb-2">Results</label>
                      <select
                        value={filters.limit}
                        onChange={(e) => setFilters({ ...filters, limit: parseInt(e.target.value) })}
                        className="w-full rounded-lg bg-background-elevated border border-background-border px-4 py-3 text-sm text-foreground focus:outline-none focus:border-accent/50 transition-colors"
                      >
                        <option value={10}>10 results</option>
                        <option value={25}>25 results</option>
                        <option value={50}>50 results</option>
                      </select>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Main Search Area */}
            <div className="space-y-6">
              {/* Search Input */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative"
              >
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-foreground-muted" />
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    placeholder="Find Python backend engineers with Docker experience..."
                    className="w-full rounded-lg bg-background-elevated border border-background-border pl-12 pr-32 py-4 text-foreground placeholder-foreground-subtle focus:outline-none focus:border-accent/50 transition-colors"
                  />
                  <button
                    onClick={handleSearch}
                    disabled={loading || !query.trim()}
                    className="absolute right-2 top-1/2 -translate-y-1/2 inline-flex items-center justify-center h-10 px-6 rounded-lg bg-accent hover:bg-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <Search className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </motion.div>

              {/* Loading State */}
              {loading && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-xl bg-background-card border border-background-border p-12 text-center"
                >
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="h-12 w-12 rounded-full border-4 border-accent border-t-transparent mx-auto mb-4"
                  />
                  <p className="text-foreground-muted">Searching candidates...</p>
                </motion.div>
              )}

              {/* No Results */}
              {!loading && results.length === 0 && query && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-xl bg-background-card border border-background-border p-12 text-center"
                >
                  <div className="inline-flex h-16 w-16 items-center justify-center rounded-lg bg-accent/10 mb-4">
                    <Search className="h-8 w-8 text-accent" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">No candidates found</h3>
                  <p className="text-foreground-muted">Try adjusting your search or filters</p>
                </motion.div>
              )}

              {/* Results */}
              {!loading && results.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4"
                >
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-foreground-muted">{results.length} candidates found</div>
                    <div className="flex items-center gap-2 text-sm text-accent">
                      <Zap className="h-4 w-4" />
                      AI Ranked
                    </div>
                  </div>

                  {results.map((result, i) => (
                    <motion.div
                      key={result.candidate_id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="group rounded-xl bg-background-card border border-background-border p-6 hover:border-accent/50 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-3">
                            <div className="h-12 w-12 rounded-lg bg-accent/20 flex items-center justify-center text-xl font-bold text-accent">
                              {result.payload?.full_name?.charAt(0) || "?"}
                            </div>
                            <div>
                              <h3 className="text-lg font-semibold">{result.payload?.full_name || "Unknown"}</h3>
                              <div className="flex items-center gap-2 mt-1">
                                <div className="inline-flex items-center gap-1 rounded-lg bg-accent/10 border border-accent/20 px-3 py-1 text-sm font-medium text-accent">
                                  <Star className="h-4 w-4 fill-accent" />
                                  {Math.round(result.score)}% match
                                </div>
                                <div className="inline-flex items-center gap-1 rounded-lg bg-success/10 border border-success/20 px-3 py-1 text-sm text-success">
                                  <Target className="h-3 w-3" />
                                  High relevance
                                </div>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center gap-4 text-sm text-foreground-muted mb-3">
                            {result.payload?.location && (
                              <div className="flex items-center gap-2">
                                <MapPin className="h-4 w-4" />
                                {result.payload.location}
                              </div>
                            )}
                            {result.payload?.headline && (
                              <div className="flex items-center gap-2">
                                <Briefcase className="h-4 w-4" />
                                {result.payload.headline}
                              </div>
                            )}
                          </div>

                          <div className="flex flex-wrap gap-2 mb-3">
                            {result.payload?.skills?.slice(0, 6).map((skill: string) => (
                              <span
                                key={skill}
                                className="inline-flex items-center rounded-lg bg-background-elevated border border-background-border px-3 py-1 text-sm text-foreground"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>

                          <p className="text-sm text-foreground-muted line-clamp-2">{result.snippet}</p>
                        </div>

                        <Link
                          href={`/candidates/${result.candidate_id}`}
                          className="flex-shrink-0 inline-flex items-center justify-center h-10 w-10 rounded-lg bg-background-card border border-background-border hover:bg-background-elevated transition-colors"
                        >
                          <ArrowUpRight className="h-5 w-5" />
                        </Link>
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              )}

              {/* Empty State */}
              {!loading && results.length === 0 && !query && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-xl bg-background-card border border-background-border p-12 text-center"
                >
                  <div className="inline-flex h-16 w-16 items-center justify-center rounded-lg bg-accent/10 mb-4">
                    <Search className="h-8 w-8 text-accent" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Start your search</h3>
                  <p className="text-foreground-muted mb-6">
                    Enter a natural language query to find candidates using AI-powered semantic search
                  </p>
                  <div className="text-left max-w-md mx-auto">
                    <p className="text-sm font-medium text-foreground mb-3">Try:</p>
                    <div className="space-y-2">
                      {suggestedQueries.map((suggestedQuery, i) => (
                        <button
                          key={i}
                          onClick={() => setQuery(suggestedQuery)}
                          className="block w-full text-left rounded-lg bg-background-card border border-background-border px-4 py-3 text-sm text-foreground hover:bg-background-elevated hover:border-accent/50 transition-colors"
                        >
                          "{suggestedQuery}"
                        </button>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
