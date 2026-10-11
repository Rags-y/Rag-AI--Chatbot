
"use client";

import { useState, type FormEvent, type KeyboardEvent } from "react";
import {
  ArrowUp,
  Bot,
  BookOpen,
  Check,
  ChevronDown,
  CircleHelp,
  FileText,
  MessageSquare,
  Plus,
  Settings,
  Sparkles,
  Trash2,
  UserRound,
  Zap,
} from "lucide-react";

type Message = {
  id: number;
  role: "user" | "assistant";
  content: string;
  sources?: number[];
};

const suggestions = [
  {
    icon: BookOpen,
    title: "Explain Agentic AI",
    description: "Understand the fundamentals and how it works.",
    prompt: "What is Agentic AI?",
  },
  {
    icon: Zap,
    title: "How do AI agents work?",
    description: "Explore planning, reasoning, and decision-making.",
    prompt: "How do AI agents work?",
  },
  {
    icon: FileText,
    title: "Key characteristics",
    description: "Discover the main capabilities of AI agents.",
    prompt: "What are the key characteristics of Agentic AI?",
  },
  {
    icon: MessageSquare,
    title: "Real-world applications",
    description: "See where agentic systems can be used.",
    prompt: "What are the real-world applications of Agentic AI?",
  },
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function sendMessage(text: string) {
    const question = text.trim();

    if (!question || loading) return;

    // Preserve the previous conversation for follow-up questions.
    const previousMessages = messages;

    setError("");
    setMessages((previous) => [
      ...previous,
      {
        id: Date.now(),
        role: "user",
        content: question,
      },
    ]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          chat_history: previousMessages.map(({ role, content }) => ({
            role,
            content,
          })),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const detail =
          typeof errorData?.detail === "string"
            ? errorData.detail
            : `Request failed with status ${response.status}`;

        throw new Error(detail);
      }

      const data: { answer: string; sources: number[] } =
        await response.json();

      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          role: "assistant",
          content: data.answer,
          sources: Array.isArray(data.sources) ? data.sources : [],
        },
      ]);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "An unexpected error occurred.";

      setError(message);
      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          role: "assistant",
          content:
            "I couldn't get a response from the backend. Please check that the FastAPI server is running on port 8000 and try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendMessage(input);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void sendMessage(input);
    }
  }

  function clearChat() {
    if (loading) return;
    setMessages([]);
    setInput("");
    setError("");
  }

  return (
    <main className="flex h-dvh overflow-hidden bg-[#101014] text-[#f4f4f5]">
      {/* Sidebar */}
      <aside className="hidden w-[250px] shrink-0 flex-col border-r border-white/[0.07] bg-[#0c0c10] p-4 md:flex">
        <div className="mb-8 flex items-center gap-3 px-2 pt-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-500/15 text-violet-300">
            <Sparkles size={23} />
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight">Nexa AI</h1>
            <p className="text-xs text-zinc-500">Document intelligence</p>
          </div>
        </div>

        <button
          onClick={clearChat}
          disabled={loading}
          className="flex items-center justify-center gap-2 rounded-xl bg-violet-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-violet-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Plus size={17} />
          New conversation
        </button>

        <div className="mt-8">
          <p className="mb-3 px-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-zinc-500">
            Workspace
          </p>
          <div className="flex items-center gap-3 rounded-lg bg-white/[0.05] px-3 py-3 text-sm text-zinc-200">
            <MessageSquare size={17} className="text-violet-300" />
            Agentic AI Chat
          </div>
        </div>

        <div className="mt-8 rounded-xl border border-white/[0.07] bg-white/[0.025] p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-medium">
            <FileText size={17} className="text-violet-300" />
            Knowledge source
          </div>
          <p className="text-xs leading-5 text-zinc-400">
            Agentic AI.pdf
          </p>
          <div className="mt-3 flex items-center gap-2 text-[11px] text-emerald-400">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            RAG knowledge base
          </div>
        </div>

        <div className="mt-auto space-y-1 border-t border-white/[0.07] pt-4">
          <div className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-zinc-400">
            <Settings size={17} />
            Settings
          </div>
          <div className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-zinc-400">
            <CircleHelp size={17} />
            Help
          </div>
          <div className="mt-4 flex items-center gap-3 rounded-xl bg-white/[0.035] p-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-violet-500/15 text-violet-300">
              <UserRound size={18} />
            </div>
            <div>
              <p className="text-sm font-medium">Personal workspace</p>
              <p className="text-xs text-zinc-500">AI assistant</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main chat area */}
      <section className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-[68px] shrink-0 items-center justify-between border-b border-white/[0.07] px-5 md:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-500/10 text-violet-300 md:hidden">
              <Sparkles size={20} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-semibold">Agentic AI Chat</h2>
                <ChevronDown size={15} className="text-zinc-500" />
              </div>
              <p className="mt-0.5 text-xs text-zinc-500">
                Ask questions about your document
              </p>
            </div>
          </div>

          <button
            onClick={clearChat}
            disabled={loading || messages.length === 0}
            title="Clear conversation"
            className="flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-xs text-zinc-400 transition hover:bg-white/[0.06] hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Trash2 size={14} />
            <span className="hidden sm:inline">Clear chat</span>
          </button>
        </header>

        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="mx-auto flex min-h-full w-full max-w-4xl flex-col justify-center px-5 py-10 sm:px-8">
              <div className="mb-7 flex h-14 w-14 items-center justify-center rounded-2xl border border-violet-400/20 bg-gradient-to-br from-violet-500/20 to-indigo-500/10 text-violet-300 shadow-lg shadow-violet-950/20">
                <Sparkles size={27} />
              </div>

              <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-violet-300">
                Your AI knowledge assistant
              </p>
              <h2 className="max-w-2xl text-3xl font-semibold leading-tight tracking-tight sm:text-5xl">
                Ask anything.
                <br />
                <span className="text-zinc-500">Understand everything.</span>
              </h2>
              <p className="mt-5 max-w-xl text-sm leading-7 text-zinc-400 sm:text-base">
                Explore Agentic AI using answers generated from your document.
                Ask a question, dig deeper, and discover relevant information.
              </p>

              <div className="mt-10 grid gap-3 sm:grid-cols-2">
                {suggestions.map((suggestion) => {
                  const Icon = suggestion.icon;

                  return (
                    <button
                      key={suggestion.title}
                      onClick={() => void sendMessage(suggestion.prompt)}
                      disabled={loading}
                      className="group rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4 text-left transition hover:border-violet-400/30 hover:bg-violet-500/[0.06] disabled:opacity-50"
                    >
                      <div className="mb-4 flex h-9 w-9 items-center justify-center rounded-xl bg-white/[0.06] text-violet-300 transition group-hover:bg-violet-500/15">
                        <Icon size={18} />
                      </div>
                      <p className="text-sm font-medium">{suggestion.title}</p>
                      <p className="mt-1.5 text-xs leading-5 text-zinc-500">
                        {suggestion.description}
                      </p>
                    </button>
                  );
                })}
              </div>

              <p className="mt-7 text-center text-[11px] text-zinc-600">
                Powered by retrieval-augmented generation
              </p>
            </div>
          ) : (
            <div className="mx-auto w-full max-w-4xl space-y-8 px-5 py-8 sm:px-8 sm:py-10">
              {messages.map((message) => (
                <article key={message.id} className="flex gap-3 sm:gap-4">
                  <div
                    className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${
                      message.role === "assistant"
                        ? "bg-violet-500/15 text-violet-300"
                        : "bg-white/[0.08] text-zinc-300"
                    }`}
                  >
                    {message.role === "assistant" ? (
                      <Bot size={19} />
                    ) : (
                      <UserRound size={18} />
                    )}
                  </div>

                  <div className="min-w-0 flex-1 pt-1">
                    <div className="mb-2 text-xs font-semibold text-zinc-300">
                      {message.role === "assistant" ? "Nexa AI" : "You"}
                    </div>
                    <div className="whitespace-pre-wrap break-words text-sm leading-7 text-zinc-200">
                      {message.content}
                    </div>

                    {message.role === "assistant" &&
                      message.sources &&
                      message.sources.length > 0 && (
                        <div className="mt-5 border-t border-white/[0.07] pt-3">
                          <div className="mb-2 flex items-center gap-2 text-[11px] font-medium text-zinc-500">
                            <BookOpen size={13} />
                            Retrieved source pages
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {message.sources.map((page, index) => (
                              <span
                                key={`${page}-${index}`}
                                className="rounded-md border border-violet-400/15 bg-violet-400/[0.06] px-2 py-1 text-[11px] text-violet-300"
                              >
                                Page {page}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                  </div>
                </article>
              ))}

              {loading && (
                <div className="flex gap-3 sm:gap-4">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-violet-500/15 text-violet-300">
                    <Bot size={19} />
                  </div>
                  <div className="pt-2">
                    <p className="mb-3 text-xs font-semibold text-zinc-300">
                      Nexa AI
                    </p>
                    <div className="flex items-center gap-2 text-sm text-zinc-500">
                      <span className="flex gap-1">
                        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-violet-400" />
                        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-violet-400 [animation-delay:150ms]" />
                        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-violet-400 [animation-delay:300ms]" />
                      </span>
                      Searching your knowledge base...
                    </div>
                  </div>
                </div>
              )}

              {error && (
                <p className="ml-12 text-xs text-amber-400">
                  Request detail: {error}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Message composer */}
        <div className="shrink-0 px-4 pb-5 pt-3 sm:px-8 sm:pb-7">
          <form
            onSubmit={handleSubmit}
            className="mx-auto max-w-4xl rounded-2xl border border-white/[0.12] bg-[#18181e] shadow-xl shadow-black/10 transition focus-within:border-violet-400/40"
          >
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about Agentic AI..."
              rows={2}
              disabled={loading}
              className="block max-h-40 min-h-[76px] w-full resize-y bg-transparent px-4 pb-2 pt-4 text-sm leading-6 text-zinc-100 outline-none placeholder:text-zinc-600 disabled:opacity-60 sm:px-5"
            />

            <div className="flex items-center justify-between px-3 pb-3 sm:px-4">
              <div className="flex items-center gap-2 pl-1 text-[11px] text-zinc-500">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                Document-grounded answers
              </div>

              <button
                type="submit"
                disabled={!input.trim() || loading}
                aria-label="Send message"
                className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-500 text-white transition hover:bg-violet-400 disabled:cursor-not-allowed disabled:bg-white/[0.07] disabled:text-zinc-600"
              >
                <ArrowUp size={19} />
              </button>
            </div>
          </form>

          <p className="mx-auto mt-3 max-w-4xl text-center text-[10px] leading-5 text-zinc-600">
            AI-generated responses can make mistakes. Verify important
            information against the source document.
          </p>
        </div>
      </section>
    </main>
  );
}
