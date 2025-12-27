import { create } from 'zustand';
import { ChatMessage, DynamicView, ConnectionState } from '@/types/jarvis';

interface ChatState {
    // Messages
    messages: ChatMessage[];
    addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
    updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
    clearMessages: () => void;

    // Connection
    connectionState: ConnectionState;
    setConnectionState: (state: ConnectionState) => void;

    // Dynamic View
    dynamicView: DynamicView | null;
    setDynamicView: (view: DynamicView | null) => void;

    // Input
    inputValue: string;
    setInputValue: (value: string) => void;

    // Thinking state
    isThinking: boolean;
    setIsThinking: (thinking: boolean) => void;
}

export const useChatStore = create<ChatState>((set) => ({
    // Messages
    messages: [],
    addMessage: (message) =>
        set((state) => ({
            messages: [
                ...state.messages,
                {
                    ...message,
                    id: crypto.randomUUID(),
                    timestamp: new Date(),
                },
            ],
        })),
    updateMessage: (id, updates) =>
        set((state) => ({
            messages: state.messages.map((msg) =>
                msg.id === id ? { ...msg, ...updates } : msg
            ),
        })),
    clearMessages: () => set({ messages: [] }),

    // Connection
    connectionState: 'disconnected',
    setConnectionState: (connectionState) => set({ connectionState }),

    // Dynamic View
    dynamicView: null,
    setDynamicView: (dynamicView) => set({ dynamicView }),

    // Input
    inputValue: '',
    setInputValue: (inputValue) => set({ inputValue }),

    // Thinking
    isThinking: false,
    setIsThinking: (isThinking) => set({ isThinking }),
}));
