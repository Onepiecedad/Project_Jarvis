'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { useChatStore } from '@/stores/chatStore';

// Use Next.js proxy to avoid CORS issues
const JARVIS_API_URL = '/api/jarvis';
const POLL_INTERVAL = 3000; // Poll every 3 seconds to reduce connection overload

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
    log_progress: number;
    log_progress_active: boolean;
    paused: boolean;
}

interface MessageResponse {
    message: string;
    context: string;
}

export function useJarvisApi() {
    const [contextId, setContextIdState] = useState<string>('');
    const contextIdRef = useRef<string>(''); // Keep in sync for polling
    const [isConnected, setIsConnected] = useState(false);
    const pollTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const logFromRef = useRef<number>(0);
    const isPollingRef = useRef(false);
    const shownLogIdsRef = useRef<Set<string>>(new Set()); // Track shown messages

    // Wrapper to update both state and ref
    const setContextId = (id: string) => {
        contextIdRef.current = id;
        setContextIdState(id);
    };

    const {
        setConnectionState,
        addMessage,
        setIsThinking,
    } = useChatStore();

    // CSRF token state
    const csrfTokenRef = useRef<string>('');

    // Get CSRF token
    const getCsrfToken = useCallback(async (): Promise<string> => {
        if (csrfTokenRef.current) return csrfTokenRef.current;

        try {
            const response = await fetch(`${JARVIS_API_URL}/csrf_token`, {
                credentials: 'include',
            });
            if (response.ok) {
                const data = await response.json();
                if (data.ok && data.token) {
                    csrfTokenRef.current = data.token;
                    return data.token;
                }
            }
        } catch (error) {
            console.error('Failed to get CSRF token:', error);
        }
        return '';
    }, []);

    // Make API request with CSRF token and credentials
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
            // If CSRF error, clear token and retry once
            if (response.status === 403) {
                csrfTokenRef.current = '';
                const newToken = await getCsrfToken();
                const retryResponse = await fetch(`${JARVIS_API_URL}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': newToken,
                    },
                    credentials: 'include',
                    body: JSON.stringify(data || {}),
                });
                if (!retryResponse.ok) {
                    throw new Error(`API error: ${retryResponse.status}`);
                }
                return retryResponse.json();
            }
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
                context: contextIdRef.current,
                log_from: logFromRef.current,
            });

            setIsConnected(true);
            setConnectionState('connected');

            // Always update context ID from poll response to stay in sync
            if (response.context && response.context !== contextIdRef.current) {
                setContextId(response.context);
                // Reset log position when context changes
                logFromRef.current = 0;
                shownLogIdsRef.current.clear();
            }

            // Use Agent Zero's progress indicator for thinking state
            setIsThinking(response.log_progress_active || false);

            // Process new log entries
            if (response.logs && response.logs.length > 0) {
                for (const log of response.logs) {
                    // Use log.no as unique identifier since log.id can be null
                    const logKey = `${response.context}-${log.no}`;

                    // Skip if we've already processed this log
                    if (shownLogIdsRef.current.has(logKey)) {
                        continue;
                    }

                    // Update log position
                    logFromRef.current = Math.max(logFromRef.current, log.no + 1);

                    // Handle different log types
                    switch (log.type) {
                        case 'response':
                            // This is the final response from JARVIS
                            if (log.content && !log.temp) {
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

                                if (displayContent) {
                                    shownLogIdsRef.current.add(logKey);
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
                                    shownLogIdsRef.current.add(logKey);
                                    addMessage({
                                        role: 'assistant',
                                        content: log.content,
                                    });
                                }
                            }
                            break;

                        case 'tool':
                            // Tool execution - just log for now
                            console.log('Tool:', log.heading, log.content);
                            break;

                        case 'hint':
                        case 'info':
                        case 'util':
                            // These are handled by log_progress_active
                            break;

                        case 'error':
                        case 'warning':
                            if (log.content && !log.temp) {
                                shownLogIdsRef.current.add(logKey);
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
    }, [apiRequest, addMessage, setIsThinking, setConnectionState]);

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
                context: contextIdRef.current,
            });

            // Update context ID if received (and reset logs if it changed)
            if (response.context && response.context !== contextIdRef.current) {
                setContextId(response.context);
                logFromRef.current = 0;
                shownLogIdsRef.current.clear();
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
    }, [apiRequest, addMessage, setIsThinking]);

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
