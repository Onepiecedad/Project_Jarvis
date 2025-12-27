'use client';

import { useEffect, useRef, useCallback } from 'react';
import { useChatStore } from '@/stores/chatStore';
import { JarvisMessage, JarvisResponse } from '@/types/jarvis';

const JARVIS_WS_URL = process.env.NEXT_PUBLIC_JARVIS_WS_URL || 'ws://localhost:50080/ws';

export function useJarvisSocket() {
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const {
        setConnectionState,
        addMessage,
        updateMessage,
        setIsThinking,
        setDynamicView,
        messages,
    } = useChatStore();

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        setConnectionState('connecting');

        try {
            wsRef.current = new WebSocket(JARVIS_WS_URL);

            wsRef.current.onopen = () => {
                console.log('🟢 Connected to JARVIS');
                setConnectionState('connected');

                // Clear any pending reconnect
                if (reconnectTimeoutRef.current) {
                    clearTimeout(reconnectTimeoutRef.current);
                    reconnectTimeoutRef.current = null;
                }
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const response: JarvisResponse = JSON.parse(event.data);
                    handleMessage(response);
                } catch (error) {
                    console.error('Failed to parse JARVIS response:', error);
                }
            };

            wsRef.current.onclose = () => {
                console.log('🔴 Disconnected from JARVIS');
                setConnectionState('disconnected');

                // Attempt reconnect after 5 seconds
                reconnectTimeoutRef.current = setTimeout(() => {
                    console.log('🔄 Attempting to reconnect...');
                    connect();
                }, 5000);
            };

            wsRef.current.onerror = (error) => {
                console.error('WebSocket error:', error);
                setConnectionState('error');
            };
        } catch (error) {
            console.error('Failed to connect to JARVIS:', error);
            setConnectionState('error');
        }
    }, [setConnectionState]);

    const handleMessage = useCallback((response: JarvisResponse) => {
        switch (response.type) {
            case 'text':
                setIsThinking(false);
                addMessage({
                    role: 'assistant',
                    content: response.content || '',
                });
                break;

            case 'thinking':
                setIsThinking(true);
                break;

            case 'render':
                setDynamicView({
                    type: response.component as 'table' | 'card' | 'list' | 'form' | 'chart' | 'empty',
                    title: response.message,
                    data: response.data,
                });
                break;

            case 'navigate':
                // Handle navigation (could use Next.js router)
                console.log('Navigate to:', response.path, response.filters);
                break;

            case 'notification':
                // TODO: Implement toast notifications
                console.log(`[${response.level}] ${response.message}`);
                break;

            case 'tool_call':
                // Show tool being called
                const lastMessage = messages[messages.length - 1];
                if (lastMessage?.role === 'assistant') {
                    updateMessage(lastMessage.id, {
                        toolCalls: [
                            ...(lastMessage.toolCalls || []),
                            {
                                tool: response.tool_name || 'unknown',
                                args: response.tool_args || {},
                                status: 'running',
                            },
                        ],
                    });
                }
                break;

            case 'tool_result':
                // Update tool result
                const msg = messages[messages.length - 1];
                if (msg?.toolCalls) {
                    const updatedCalls = msg.toolCalls.map((call, idx) =>
                        idx === msg.toolCalls!.length - 1
                            ? { ...call, result: response.tool_result, status: 'completed' as const }
                            : call
                    );
                    updateMessage(msg.id, { toolCalls: updatedCalls });
                }
                break;

            case 'error':
                setIsThinking(false);
                addMessage({
                    role: 'assistant',
                    content: `❌ Error: ${response.message || 'Unknown error'}`,
                });
                break;
        }
    }, [addMessage, updateMessage, setIsThinking, setDynamicView, messages]);

    const sendMessage = useCallback((content: string) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.error('WebSocket is not connected');
            return false;
        }

        const message: JarvisMessage = {
            type: 'user_message',
            content,
            context: {
                timestamp: new Date().toISOString(),
                source: 'dashboard',
            },
        };

        wsRef.current.send(JSON.stringify(message));

        // Add user message to chat
        addMessage({
            role: 'user',
            content,
        });

        setIsThinking(true);
        return true;
    }, [addMessage, setIsThinking]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setConnectionState('disconnected');
    }, [setConnectionState]);

    // Connect on mount
    useEffect(() => {
        connect();
        return () => disconnect();
    }, [connect, disconnect]);

    return {
        sendMessage,
        connect,
        disconnect,
        isConnected: useChatStore((state) => state.connectionState === 'connected'),
        connectionState: useChatStore((state) => state.connectionState),
    };
}
