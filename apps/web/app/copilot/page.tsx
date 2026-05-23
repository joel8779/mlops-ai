"use client";

import { useState, useRef, useEffect } from "react";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Bot, Send, User, Loader2, Sparkles } from "lucide-react";
import { aiApi } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: string[];
  confidence?: number;
}

export default function CopilotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your AI recruiting copilot. I can help you with candidate searches, interview questions, comparisons, and insights. What would you like to know?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

    try {
      const response = await aiApi.copilot({
        query: input,
        context: {},
        top_k: 5,
      }) as any;

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        citations: response.usage?.citations,
        confidence: response.usage?.confidence,
      };

      setMessages((prev) => [...prev, assistantMessage]);
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
    "Find top backend engineers",
    "Generate interview questions",
    "Compare candidates",
    "Explain ranking scores",
  ];

  return (
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <div className="flex items-center gap-2">
          <Bot size={24} className="text-signal" />
          <div>
            <h1 className="text-xl font-semibold">Recruiter AI Copilot</h1>
            <p className="text-sm text-slate-600">RAG-backed answers with candidate citations</p>
          </div>
        </div>
      </header>
      <section className="mx-auto max-w-4xl p-6">
        <div className="min-h-[500px] rounded-md border border-slate-200 bg-white p-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.role === "assistant" && (
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-signal/10">
                    <Bot size={16} className="text-signal" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-3 ${
                    message.role === "user"
                      ? "bg-signal text-white"
                      : "bg-slate-50 text-slate-900"
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  {message.citations && message.citations.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-slate-200">
                      <div className="flex items-center gap-1 text-xs text-slate-600">
                        <Sparkles size={12} />
                        Sources: {message.citations.length}
                      </div>
                    </div>
                  )}
                  {message.confidence !== undefined && (
                    <div className="mt-2 text-xs text-slate-600">
                      Confidence: {Math.round(message.confidence * 100)}%
                    </div>
                  )}
                </div>
                {message.role === "user" && (
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200">
                    <User size={16} className="text-slate-600" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-3 justify-start">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-signal/10">
                  <Bot size={16} className="text-signal" />
                </div>
                <div className="rounded-lg bg-slate-50 px-4 py-3">
                  <Loader2 className="animate-spin text-signal" size={16} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {messages.length === 1 && (
          <div className="mt-4">
            <p className="text-sm font-medium text-slate-700 mb-2">Quick actions:</p>
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action) => (
                <button
                  key={action}
                  onClick={() => setInput(action)}
                  className="rounded-full border border-slate-300 px-3 py-1 text-sm text-slate-700 hover:border-signal hover:text-signal"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="mt-3 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about candidates, rankings, or hiring insights..."
            className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-2 outline-none"
            disabled={loading}
          />
          <Button onClick={handleSend} disabled={loading || !input.trim()}>
            {loading ? <Loader2 className="animate-spin" size={16} /> : <Send size={16} />}
          </Button>
        </div>
      </section>
    </AppShell>
  );
}
