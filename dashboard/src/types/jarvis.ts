// WebSocket message types for JARVIS communication

export interface JarvisMessage {
    type: 'user_message' | 'context_update' | 'command';
    content?: string;
    context?: Record<string, unknown>;
    command?: string;
    args?: Record<string, unknown>;
}

export interface JarvisResponse {
    type: 'text' | 'render' | 'navigate' | 'notification' | 'thinking' | 'tool_call' | 'tool_result' | 'error';
    content?: string;
    component?: string;
    data?: unknown;
    path?: string;
    filters?: Record<string, unknown>;
    level?: 'info' | 'success' | 'warning' | 'error';
    message?: string;
    tool_name?: string;
    tool_args?: Record<string, unknown>;
    tool_result?: string;
}

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    isThinking?: boolean;
    toolCalls?: ToolCall[];
}

export interface ToolCall {
    tool: string;
    args: Record<string, unknown>;
    result?: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
}

export interface DynamicView {
    type: 'table' | 'card' | 'list' | 'form' | 'chart' | 'empty';
    title?: string;
    data?: unknown;
    columns?: Column[];
    actions?: Action[];
}

export interface Column {
    key: string;
    label: string;
    type?: 'text' | 'number' | 'date' | 'status' | 'actions';
}

export interface Action {
    label: string;
    action: string;
    icon?: string;
    variant?: 'primary' | 'secondary' | 'danger';
}

// Connection state
export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';
