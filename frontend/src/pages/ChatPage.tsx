import React, { useState, useRef, useEffect } from 'react';
import { Send, StopCircle, User, Bot, Paperclip } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useSettingsStore } from '../store/useStore';
import { Message } from '../types';
import { Button } from '../components/ui/Button';
import { cn } from '../lib/utils';

const ChatPage: React.FC = () => {
  const { provider, model } = useSettingsStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    const botMsgId = (Date.now() + 1).toString();
    const botMsgPlaceholder: Message = {
      id: botMsgId,
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, botMsgPlaceholder]);

    abortControllerRef.current = new AbortController();

    try {
      // Direct fetch to support streaming
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg.content,
          model: model,
          provider: provider,
          stream: true,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok || !response.body) {
        throw new Error('Network response was not ok');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let accumalatedContent = '';

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        const chunkValue = decoder.decode(value, { stream: !done });

        // Simple parsing assumption: backend sends raw text chunks or json lines
        // If the backend sends SSE (Server Sent Events), this parsing logic needs to be adapted.
        // Assuming raw text stream or NDJSON for this demo as per "Streaming response handling"
        accumalatedContent += chunkValue;

        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMsgId ? { ...msg, content: accumalatedContent } : msg
          )
        );
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Fetch aborted');
      } else {
        console.error('Error:', error);
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: `**Error**: Failed to connect to backend at \`localhost:8000\`. Please ensure the backend server is running.`,
            timestamp: Date.now(),
          },
        ]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-8">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center opacity-40">
            <div className="w-16 h-16 bg-zinc-100 rounded-2xl flex items-center justify-center mb-4">
              <SparklesIcon className="w-8 h-8 text-zinc-400" />
            </div>
            <h2 className="text-xl font-semibold text-zinc-900">How can I help you today?</h2>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={cn(
                "flex w-full gap-4",
                msg.role === 'user' ? "justify-end" : "justify-start"
              )}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-indigo-100 flex-shrink-0 flex items-center justify-center border border-indigo-200 mt-1">
                  <Bot className="w-5 h-5 text-indigo-600" />
                </div>
              )}

              <div className={cn(
                "relative max-w-[80%] rounded-2xl px-5 py-3 text-sm leading-relaxed",
                msg.role === 'user'
                  ? "bg-zinc-100 text-zinc-900 rounded-br-sm"
                  : "bg-white text-zinc-800 shadow-sm border border-zinc-100 rounded-bl-sm"
              )}>
                {msg.role === 'user' ? (
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                ) : (
                  <div className="markdown-body">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        code({ className, children, ...props }) {
                          return (
                            <code className={cn("bg-zinc-100 px-1 py-0.5 rounded text-zinc-800 font-mono text-xs", className)} {...props}>
                              {children}
                            </code>
                          )
                        },
                        pre({ children }) {
                          return <pre className="bg-zinc-900 text-zinc-50 p-3 rounded-lg overflow-x-auto my-2 text-xs font-mono">{children}</pre>
                        }
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-zinc-200 flex-shrink-0 flex items-center justify-center border border-zinc-300 mt-1">
                  <User className="w-5 h-5 text-zinc-600" />
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 sm:p-6 bg-white">
        <div className="relative max-w-3xl mx-auto shadow-lg rounded-2xl border border-zinc-200 bg-white focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-400 transition-all">
          <form onSubmit={handleSubmit} className="flex flex-col">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything..."
              className="w-full min-h-[60px] max-h-[200px] p-4 pr-12 bg-transparent border-none resize-none focus:ring-0 text-zinc-800 placeholder:text-zinc-400"
              style={{ height: 'auto', overflow: 'hidden' }}
            />

            <div className="flex items-center justify-between px-2 pb-2">
              <div className="flex items-center">
                <Button type="button" variant="ghost" size="icon" className="text-zinc-400 hover:text-zinc-600">
                  <Paperclip className="w-5 h-5" />
                </Button>
              </div>
              <div>
                {isLoading ? (
                  <Button type="button" onClick={handleStop} variant="ghost" size="icon" className="text-red-500 hover:bg-red-50">
                    <StopCircle className="w-6 h-6" />
                  </Button>
                ) : (
                  <Button type="submit" disabled={!input.trim()} size="icon" variant="primary" className="rounded-xl w-9 h-9">
                    <Send className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
          </form>
        </div>
        <p className="text-center text-xs text-zinc-400 mt-3">
          Mind-Q can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
};

// Helper for empty state icon
function SparklesIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
    </svg>
  );
}

export default ChatPage;