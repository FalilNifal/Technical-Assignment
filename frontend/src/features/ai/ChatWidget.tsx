import { useEffect, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Bot, MessageSquare, Send, Sparkles, X } from "lucide-react";
import { Button } from "../../components/ui/Button";
import { getApiErrorMessage } from "../../lib/apiClient";
import { sendChat, type ChatMessage } from "./chat.api";

const SUGGESTIONS = [
  "What did the team work on last week?",
  "Any recurring blockers this week?",
  "Who hasn't submitted a report yet?",
];

const GREETING: ChatMessage = {
  role: "assistant",
  content: "Hi! Ask me about your team's activity, blockers, or workload and I'll answer from the submitted reports.",
};

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING]);
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const mutation = useMutation({
    mutationFn: (history: ChatMessage[]) => sendChat(history),
    onSuccess: (data) => {
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply }]);
      setError("");
    },
    onError: (err) => setError(getApiErrorMessage(err)),
  });

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, mutation.isPending, open]);

  function ask(text: string) {
    const question = text.trim();
    if (!question || mutation.isPending) return;
    // Send only real turns to the API (skip the local greeting).
    const history: ChatMessage[] = [...messages.filter((m) => m !== GREETING), { role: "user", content: question }];
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    mutation.mutate(history);
  }

  return (
    <>
      {/* Launcher */}
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label="Open AI assistant"
        className="fixed bottom-20 right-4 z-50 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 via-fuchsia-500 to-cyan-500 text-white shadow-glow-violet transition hover:-translate-y-0.5 hover:brightness-110 lg:bottom-6 lg:right-6"
      >
        {open ? <X className="h-6 w-6" /> : <MessageSquare className="h-6 w-6" />}
      </button>

      {open && (
        <div className="fixed bottom-36 right-4 z-50 flex h-[32rem] w-[min(24rem,calc(100vw-2rem))] flex-col overflow-hidden rounded-3xl border border-white/70 bg-white/95 shadow-panel ring-1 ring-slate-900/5 backdrop-blur-xl animate-slide-up lg:bottom-24 lg:right-6">
          {/* Header */}
          <div className="flex items-center justify-between gap-3 bg-gradient-to-r from-violet-600 via-fuchsia-500 to-cyan-500 px-4 py-3 text-white">
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-white/20 ring-1 ring-white/25">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-bold leading-tight">PulseBoard AI</p>
                <p className="text-[11px] text-white/80">Team activity assistant</p>
              </div>
            </div>
            <button type="button" onClick={() => setOpen(false)} aria-label="Close" className="rounded-xl p-1.5 transition hover:bg-white/20">
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto bg-gradient-to-b from-white to-violet-50/40 p-4">
            {messages.map((m, i) => (
              <div key={i} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
                <div
                  className={
                    m.role === "user"
                      ? "max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-br-md bg-gradient-to-r from-violet-600 to-fuchsia-500 px-3.5 py-2 text-sm text-white shadow-sm"
                      : "max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-bl-md bg-white px-3.5 py-2 text-sm leading-6 text-slate-700 shadow-sm ring-1 ring-violet-100"
                  }
                >
                  {m.content}
                </div>
              </div>
            ))}

            {mutation.isPending && (
              <div className="flex justify-start">
                <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-md bg-white px-3.5 py-3 shadow-sm ring-1 ring-violet-100">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-violet-400 [animation-delay:-0.2s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-fuchsia-400 [animation-delay:-0.1s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-400" />
                </div>
              </div>
            )}

            {error && <div className="rounded-2xl bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700 ring-1 ring-rose-100">{error}</div>}

            {messages.length <= 1 && !mutation.isPending && (
              <div className="space-y-2 pt-1">
                <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                  <Sparkles className="h-3.5 w-3.5" />Try asking
                </p>
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => ask(s)}
                    className="block w-full rounded-2xl border border-violet-100 bg-white px-3 py-2 text-left text-sm text-slate-600 transition hover:border-violet-300 hover:bg-violet-50 hover:text-violet-700"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Composer */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              ask(input);
            }}
            className="flex items-center gap-2 border-t border-slate-200 bg-white p-3"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your team..."
              className="h-11 flex-1 rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm outline-none transition focus:border-violet-400 focus:bg-white focus:ring-4 focus:ring-violet-100"
            />
            <Button type="submit" size="sm" className="h-11 w-11 p-0" isLoading={mutation.isPending} disabled={!input.trim()}>
              {!mutation.isPending && <Send className="h-4 w-4" />}
            </Button>
          </form>
        </div>
      )}
    </>
  );
}
