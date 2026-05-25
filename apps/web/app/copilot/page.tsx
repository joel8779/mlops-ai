"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Bot, 
  Send, 
  User, 
  Loader2, 
  Sparkles,
  Menu,
  Home,
  FileText,
  Settings,
  BarChart3,
  Search,
  Briefcase,
  MoreVertical,
  MessageSquare,
  Brain,
  Lightbulb,
  ChevronDown,
  Copy,
  ThumbsUp,
  ThumbsDown
} from "lucide-react";
import { aiApi } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: string[];
  confidence?: number;
  thoughts?: string[];
  isStreaming?: boolean;
}

export default function CopilotPage() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your AI recruiting copilot. I can help you with candidate searches, interview questions, comparisons, and insights. What would you like to know?",
      thoughts: ["Analyzing user intent", "Preparing recruiting context", "Loading knowledge base"],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  const simulateStreaming = async (content: string) => {
    const words = content.split(" ");
    let streamedContent = "";
    
    for (let i = 0; i < words.length; i++) {
      streamedContent += (i > 0 ? " " : "") + words[i];
      setMessages((prev) => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.role === "assistant" && lastMessage.isStreaming) {
          lastMessage.content = streamedContent;
        }
        return newMessages;
      });
      await new Promise(resolve => setTimeout(resolve, 30));
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    // Add streaming assistant message
    const streamingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: "",
      thoughts: ["Processing query", "Searching candidate database", "Generating insights"],
      isStreaming: true,
    };
    setMessages((prev) => [...prev, streamingMessage]);

    try {
      const response = await aiApi.copilot({
        query: input,
        context: {},
        top_k: 5,
      }) as any;

      await simulateStreaming(response.answer);

      setMessages((prev) => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.role === "assistant") {
          lastMessage.content = response.answer;
          lastMessage.citations = response.usage?.citations;
          lastMessage.confidence = response.usage?.confidence;
          lastMessage.isStreaming = false;
          lastMessage.thoughts = undefined;
        }
        return newMessages;
      });
    } catch (error) {
      console.error("Copilot error:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    { icon: Search, label: "Find top backend engineers", query: "Find top backend engineers with Python experience" },
    { icon: Lightbulb, label: "Generate interview questions", query: "Generate interview questions for a senior ML engineer position" },
    { icon: Briefcase, label: "Compare candidates", query: "Compare the top 3 candidates for the Senior Developer role" },
    { icon: Brain, label: "Explain ranking scores", query: "How are AI ranking scores calculated?" },
  ];

  const sidebarItems = [
    { icon: Home, label: "Dashboard", href: "/dashboard", active: false },
    { icon: Briefcase, label: "Candidates", href: "/candidates", active: false },
    { icon: Briefcase, label: "Jobs", href: "/jobs", active: false },
    { icon: FileText, label: "Resumes", href: "/resumes", active: false },
    { icon: Search, label: "Search", href: "/search", active: false },
    { icon: MessageSquare, label: "AI Copilot", href: "/copilot", active: true },
    { icon: BarChart3, label: "Analytics", href: "/analytics", active: false },
    { icon: Settings, label: "Settings", href: "/settings", active: false },
  ];


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
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-accent flex items-center justify-center">
                  <Bot className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold">AI Copilot</h1>
                  <p className="text-sm text-foreground-muted">RAG-powered recruiting assistant</p>
                </div>
              </div>
            </div>
          </div>
        </header>

        <main className="flex flex-col h-[calc(100vh-73px)]">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="mx-auto max-w-4xl space-y-6">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className={`flex gap-4 ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {message.role === "assistant" && (
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 rounded-lg bg-accent flex items-center justify-center">
                          <Bot className="h-5 w-5 text-white" />
                        </div>
                      </div>
                    )}
                    <div className={`flex-1 max-w-[80%] ${message.role === "user" ? "flex flex-col items-end" : ""}`}>
                      {/* AI Thoughts */}
                      {message.thoughts && message.thoughts.length > 0 && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          className="mb-2 rounded-lg bg-accent/10 border border-accent/20 p-3"
                        >
                          <div className="flex items-center gap-2 text-xs text-accent-subtle mb-2">
                            <Brain className="h-3 w-3" />
                            Thinking
                          </div>
                          <div className="space-y-1">
                            {message.thoughts.map((thought, i) => (
                              <motion.div
                                key={i}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.2 }}
                                className="text-xs text-foreground-muted flex items-center gap-2"
                              >
                                <div className="h-1 w-1 rounded-full bg-accent" />
                                {thought}
                              </motion.div>
                            ))}
                          </div>
                        </motion.div>
                      )}

                      {/* Message Content */}
                      <div
                        className={`rounded-xl px-6 py-4 ${
                          message.role === "user"
                            ? "bg-accent text-white"
                            : "bg-background-card border border-background-border text-foreground"
                        }`}
                      >
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                        
                        {/* Citations */}
                        {message.citations && message.citations.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-background-border">
                            <div className="flex items-center gap-2 text-xs text-foreground-muted">
                              <Sparkles className="h-3 w-3 text-accent" />
                              Sources: {message.citations.length}
                            </div>
                          </div>
                        )}

                        {/* Confidence */}
                        {message.confidence !== undefined && (
                          <div className="mt-2 text-xs text-foreground-muted">
                            Confidence: {Math.round(message.confidence * 100)}%
                          </div>
                        )}

                        {/* Actions for assistant messages */}
                        {message.role === "assistant" && !message.isStreaming && (
                          <div className="mt-3 flex gap-2">
                            <button className="p-2 rounded-lg bg-background-elevated hover:bg-background-border transition-colors">
                              <Copy className="h-4 w-4 text-foreground-muted" />
                            </button>
                            <button className="p-2 rounded-lg bg-background-elevated hover:bg-background-border transition-colors">
                              <ThumbsUp className="h-4 w-4 text-foreground-muted" />
                            </button>
                            <button className="p-2 rounded-lg bg-background-elevated hover:bg-background-border transition-colors">
                              <ThumbsDown className="h-4 w-4 text-foreground-muted" />
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                    {message.role === "user" && (
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 rounded-lg bg-background-elevated flex items-center justify-center">
                          <User className="h-5 w-5 text-foreground-muted" />
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>

              {loading && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex gap-4 justify-start"
                >
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-lg bg-accent flex items-center justify-center">
                      <Bot className="h-5 w-5 text-white" />
                    </div>
                  </div>
                  <div className="rounded-xl bg-background-card border border-background-border px-6 py-4">
                    <div className="flex gap-1">
                      {[0, 1, 2].map((i) => (
                        <motion.div
                          key={i}
                          animate={{ y: [0, -8, 0] }}
                          transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.1 }}
                          className="h-2 w-2 rounded-full bg-accent"
                        />
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Quick Actions */}
          {messages.length === 1 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="px-6 pb-4"
            >
              <p className="text-sm font-medium text-foreground-muted mb-3">Quick actions:</p>
              <div className="flex flex-wrap gap-2">
                {quickActions.map((action) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={action.label}
                      onClick={() => setInput(action.query)}
                      className="inline-flex items-center gap-2 rounded-full bg-background-card border border-background-border px-4 py-2 text-sm text-foreground hover:bg-background-elevated hover:border-accent/50 transition-colors"
                    >
                      <Icon className="h-4 w-4 text-accent" />
                      {action.label}
                    </button>
                  );
                })}
              </div>
            </motion.div>
          )}

          {/* Input */}
          <div className="p-6 border-t border-background-border bg-background/50 backdrop-blur-xl">
            <div className="mx-auto max-w-4xl">
              <div className="flex gap-3">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  placeholder="Ask about candidates, rankings, or hiring insights..."
                  className="flex-1 rounded-lg bg-background-elevated border border-background-border px-6 py-4 text-foreground placeholder-foreground-subtle focus:outline-none focus:border-accent/50 transition-colors"
                  disabled={loading}
                />
                <button
                  onClick={handleSend}
                  disabled={loading || !input.trim()}
                  className="inline-flex items-center justify-center h-14 w-14 rounded-lg bg-accent hover:bg-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Send className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
