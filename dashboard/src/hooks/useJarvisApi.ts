'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { useChatStore } from '@/stores/chatStore';

// Use Next.js proxy to avoid CORS issues
const JARVIS_API_URL = '/api/jarvis';
const POLL_INTERVAL = 1000; // Poll every second

interface LogEntry {
    no: number;
    id: string;
    type: string;
    heading?: string;
    content?: string;
    temp?: boolean;
    kvps?: Record<string, unknown>;
}

interface PollResponse {
    context: string;
    contexts: Array<{ id: string; name: string }>;
    logs: LogEntry[];
    log_guid: string;
    log_version: number;
    paused: boolean;
}

interface MessageResponse {
    message: string;
    context: string;
}

export function useJarvisApi() {
    const [contextId, setContextId] = useState<string>('');
    const [isConnected, setIsConnected] = useState(false);
    const [csrfToken, setCsrfToken] = useState<string>('');
    const pollTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const logFromRef = useRef<number>(0);
    const isPollingRef = useRef(false);

    const {
        setConnectionState,
        addMessage,
        setIsThinking,
        messages,
    } = useChatStore();

    // Get CSRF token
    const getCsrfToken = useCallback(async (): Promise<string> => {
        if (csrfToken) return csrfToken;

        try {
            const response = await fetch(`${JARVIS_API_URL}/csrf_token`, {
                credentials: 'include',
            });
            if (response.ok) {
                const data = await response.json();
                setCsrfToken(data.token);
                return data.token;
            }
        } catch (error) {
            console.error('Failed to get CSRF token:', error);
        }
        return '';
    }, [csrfToken]);

    // Make authenticated API request
    const apiRequest = useCallback(async (endpoint: string, data?: Record<string, unknown>) => {
        const token = await getCsrfToken();

        const response = await fetch(`${JARVIS_API_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': token,
            },
            credentials: 'include',
            body: JSON.stringify(data || {}),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return response.json();
    }, [getCsrfToken]);

    // Poll for updates
    const poll = useCallback(async () => {
        if (isPollingRef.current) return;
        isPollingRef.current = true;

        try {
            const response: PollResponse = await apiRequest('/poll', {
                context: contextId,
                log_from: logFromRef.current,
            });

            setIsConnected(true);
            setConnectionState('connected');

            // Update context if we got one
            if (response.context && !contextId) {
                setContextId(response.context);
            }

            // Process new log entries
            if (response.logs && response.logs.length > 0) {
                for (const log of response.logs) {
                    logFromRef.current = Math.max(logFromRef.current, log.no + 1);

                    // Handle different log types
                    switch (log.type) {
                        case 'response':
                            // This is the final response from JARVIS
                            if (log.content && !log.temp) {
                                setIsThinking(false);

                                // Try to parse JSON response and extract text
                                let displayContent = log.content;
                                try {
                                    const parsed = JSON.parse(log.content);
                                    if (parsed.tool_args?.text) {
                                        displayContent = parsed.tool_args.text;
                                    } else if (parsed.text) {
                                        displayContent = parsed.text;
                                    }
                                } catch {
                                    // Not JSON, use content as-is
                                }

                                // Check if we already have this message
                                const exists = messages.some(m => m.content === displayContent);
                                if (!exists && displayContent) {
                                    addMessage({
                                        role: 'assistant',
                                        content: displayContent,
                                    });
                                }
                            }
                            break;

                        case 'agent':
                            // Agent thinking - only show if it's a final formatted response
                            // Skip raw JSON thinking logs
                            if (log.content && !log.temp) {
                                // Check if it starts with { - if so, it's internal thinking
                                if (!log.content.trim().startsWith('{')) {
                                    const exists = messages.some(m => m.content === log.content);
                                    if (!exists) {
                                        setIsThinking(false);
                                        addMessage({
                                            role: 'assistant',
                                            content: log.content,
                                        });
                                    }
                                }
                            }
                            break;

                        case 'tool':
                            // Tool execution - could show in UI
                            console.log('Tool:', log.heading, log.content);
                            break;

                        case 'hint':
                        case 'info':
                        case 'util':
                            // Thinking/info messages - just set thinking state
                            if (log.temp) {
                                setIsThinking(true);
                            }
                            break;

                        case 'error':
                        case 'warning':
                            if (log.content && !log.temp) {
                                addMessage({
                                    role: 'assistant',
                                    content: `⚠️ ${log.content}`,
                                });
                            }
                            break;
                    }
                }
            }
        } catch (error) {
            console.error('Poll error:', error);
            setIsConnected(false);
            setConnectionState('disconnected');
        } finally {
            isPollingRef.current = false;
        }
    }, [apiRequest, contextId, addMessage, setIsThinking, setConnectionState, messages]);

    // Send message to JARVIS
    const sendMessage = useCallback(async (content: string) => {
        if (!content.trim()) return false;

        // Add user message immediately
        addMessage({
            role: 'user',
            content,
        });

        setIsThinking(true);

        try {
            const response: MessageResponse = await apiRequest('/message', {
                text: content,
                context: contextId,
            });

            // Update context ID if received
            if (response.context) {
                setContextId(response.context);
            }

            return true;
        } catch (error) {
            console.error('Failed to send message:', error);
            setIsThinking(false);
            addMessage({
                role: 'assistant',
                content: '❌ Kunde inte skicka meddelandet. Kontrollera att JARVIS körs.',
            });
            return false;
        }
    }, [apiRequest, contextId, addMessage, setIsThinking]);

    // Check connection
    const checkConnection = useCallback(async () => {
        try {
            const response = await fetch(`${JARVIS_API_URL}/health`, {
                credentials: 'include',
            });
            if (response.ok) {
                setIsConnected(true);
                setConnectionState('connected');
                return true;
            }
        } catch (error) {
            console.error('Connection check failed:', error);
        }
        setIsConnected(false);
        setConnectionState('disconnected');
        return false;
    }, [setConnectionState]);

    // Start polling
    const startPolling = useCallback(() => {
        const doPoll = async () => {
            await poll();
            pollTimeoutRef.current = setTimeout(doPoll, POLL_INTERVAL);
        };
        doPoll();
    }, [poll]);

    // Stop polling
    const stopPolling = useCallback(() => {
        if (pollTimeoutRef.current) {
            clearTimeout(pollTimeoutRef.current);
            pollTimeoutRef.current = null;
        }
    }, []);

    // Initialize connection on mount
    useEffect(() => {
        const init = async () => {
            setConnectionState('connecting');
            const connected = await checkConnection();
            if (connected) {
                startPolling();
            }
        };

        init();

        return () => {
            stopPolling();
        };
    }, [checkConnection, startPolling, stopPolling, setConnectionState]);

    return {
        sendMessage,
        isConnected,
        contextId,
        checkConnection,
    };
}
