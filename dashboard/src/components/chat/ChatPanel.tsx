'use client';

import { useRef, useEffect } from 'react';
import { Send, Loader2, Bot, User, Terminal } from 'lucide-react';
import { useChatStore } from '@/stores/chatStore';
import { useJarvisApi } from '@/hooks/useJarvisApi';
import { ChatMessage } from '@/types/jarvis';

export function ChatPanel() {
    const { messages, inputValue, setInputValue, isThinking } = useChatStore();
    const { sendMessage, isConnected } = useJarvisApi();
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputValue.trim() || !isConnected) return;

        sendMessage(inputValue.trim());
        setInputValue('');
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gradient-to-b from-slate-900 to-slate-950">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur">
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
                            <Bot className="w-5 h-5 text-white" />
                        </div>
                        <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-slate-900 ${isConnected ? 'bg-emerald-400' : 'bg-red-400'
                            }`} />
                    </div>
                    <div>
                        <h2 className="font-semibold text-white">JARVIS</h2>
                        <p className="text-xs text-slate-400">
                            {isConnected ? 'Online' : 'Offline'}
                        </p>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                    <WelcomeMessage />
                ) : (
                    messages.map((message) => (
                        <MessageBubble key={message.id} message={message} />
                    ))
                )}

                {/* Thinking indicator */}
                {isThinking && (
                    <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center flex-shrink-0">
                            <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div className="px-4 py-3 rounded-2xl rounded-tl-none bg-slate-800 border border-slate-700/50">
                            <div className="flex items-center gap-2 text-slate-400">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span className="text-sm">Tänker...</span>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-4 border-t border-slate-700/50 bg-slate-900/50">
                <div className="flex items-center gap-3">
                    <input
                        ref={inputRef}
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={isConnected ? "Skriv till JARVIS..." : "Ansluter..."}
                        disabled={!isConnected}
                        className="flex-1 px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 disabled:opacity-50 transition-all"
                    />
                    <button
                        type="submit"
                        disabled={!inputValue.trim() || !isConnected}
                        aria-label="Skicka meddelande"
                        className="p-3 rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-blue-500/25 transition-all"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </form>
        </div>
    );
}

function WelcomeMessage() {
    return (
        <div className="flex flex-col items-center justify-center h-full text-center px-8">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center mb-6 shadow-xl shadow-blue-500/20">
                <Bot className="w-10 h-10 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
                Hej, jag är JARVIS
            </h3>
            <p className="text-slate-400 max-w-sm">
                Din personliga AI-assistent för Skyland AI. Skriv vad du vill göra så hjälper jag dig.
            </p>
            <div className="mt-8 grid grid-cols-2 gap-3 w-full max-w-xs">
                <SuggestionChip text="Visa alla tasks" />
                <SuggestionChip text="Sök entities" />
                <SuggestionChip text="Skapa rapport" />
                <SuggestionChip text="Analysera data" />
            </div>
        </div>
    );
}

function SuggestionChip({ text }: { text: string }) {
    const { setInputValue } = useChatStore();

    return (
        <button
            onClick={() => setInputValue(text)}
            className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
        >
            {text}
        </button>
    );
}

function MessageBubble({ message }: { message: ChatMessage }) {
    const isUser = message.role === 'user';

    return (
        <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${isUser
                ? 'bg-gradient-to-br from-slate-600 to-slate-700'
                : 'bg-gradient-to-br from-blue-500 to-cyan-400'
                }`}>
                {isUser ? (
                    <User className="w-4 h-4 text-white" />
                ) : (
                    <Bot className="w-4 h-4 text-white" />
                )}
            </div>

            <div className={`max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
                <div className={`px-4 py-3 rounded-2xl ${isUser
                    ? 'rounded-tr-none bg-gradient-to-r from-blue-600 to-blue-500 text-white'
                    : 'rounded-tl-none bg-slate-800 border border-slate-700/50 text-slate-100'
                    }`}>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>

                {/* Tool calls */}
                {message.toolCalls && message.toolCalls.length > 0 && (
                    <div className="mt-2 space-y-2">
                        {message.toolCalls.map((call, idx) => (
                            <div key={idx} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/30 text-xs">
                                <Terminal className="w-3 h-3 text-cyan-400" />
                                <span className="text-cyan-400 font-mono">{call.tool}</span>
                                {call.status === 'running' && (
                                    <Loader2 className="w-3 h-3 animate-spin text-slate-400 ml-auto" />
                                )}
                                {call.status === 'completed' && (
                                    <span className="text-emerald-400 ml-auto">✓</span>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                <p className={`text-xs text-slate-500 mt-1 ${isUser ? 'text-right' : ''}`}>
                    {message.timestamp.toLocaleTimeString('sv-SE', { hour: '2-digit', minute: '2-digit' })}
                </p>
            </div>
        </div>
    );
}
