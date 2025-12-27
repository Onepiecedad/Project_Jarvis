import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Types for JARVIS database
export interface Agent {
    id: string;
    name: string;
    type: 'master' | 'permanent' | 'temp';
    status: 'idle' | 'busy' | 'offline';
    parent_id?: string;
    system_prompt?: string;
    config?: Record<string, unknown>;
    created_at: string;
}

export interface Task {
    id: string;
    agent_id?: string;
    title: string;
    description?: string;
    status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
    priority: number;
    result?: Record<string, unknown>;
    created_at: string;
    started_at?: string;
    completed_at?: string;
}

export interface Message {
    id: string;
    conversation_id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    metadata?: Record<string, unknown>;
    created_at: string;
}

export interface Conversation {
    id: string;
    agent_id: string;
    title?: string;
    created_at: string;
    updated_at: string;
}

export interface Entity {
    id: string;
    type: 'company' | 'person' | 'project' | 'product';
    name: string;
    properties?: Record<string, unknown>;
    created_at: string;
}

// Database helper functions
export async function getTasks(status?: string, limit = 10) {
    let query = supabase
        .from('tasks')
        .select('*, agents(name)')
        .order('created_at', { ascending: false })
        .limit(limit);

    if (status) {
        query = query.eq('status', status);
    }

    const { data, error } = await query;
    if (error) throw error;
    return data;
}

export async function getAgents() {
    const { data, error } = await supabase
        .from('agents')
        .select('*')
        .order('type', { ascending: true });

    if (error) throw error;
    return data as Agent[];
}

export async function getConversations(limit = 20) {
    const { data, error } = await supabase
        .from('conversations')
        .select('*')
        .order('updated_at', { ascending: false })
        .limit(limit);

    if (error) throw error;
    return data as Conversation[];
}

export async function getMessages(conversationId: string) {
    const { data, error } = await supabase
        .from('messages')
        .select('*')
        .eq('conversation_id', conversationId)
        .order('created_at', { ascending: true });

    if (error) throw error;
    return data as Message[];
}

export async function getEntities(type?: string, limit = 50) {
    let query = supabase
        .from('entities')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(limit);

    if (type) {
        query = query.eq('type', type);
    }

    const { data, error } = await query;
    if (error) throw error;
    return data as Entity[];
}
