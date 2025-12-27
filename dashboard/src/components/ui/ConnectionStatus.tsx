'use client';

import { useChatStore } from '@/stores/chatStore';
import { Wifi, WifiOff, RefreshCw, Circle } from 'lucide-react';
import { useJarvisApi } from '@/hooks/useJarvisApi';

export function ConnectionStatus() {
    const { connectionState } = useChatStore();
    const { checkConnection } = useJarvisApi();

    const statusConfig = {
        connecting: {
            icon: RefreshCw,
            text: 'Ansluter...',
            color: 'text-yellow-400',
            bgColor: 'bg-yellow-400/10',
            borderColor: 'border-yellow-400/20',
            animate: true,
        },
        connected: {
            icon: Wifi,
            text: 'Ansluten',
            color: 'text-emerald-400',
            bgColor: 'bg-emerald-400/10',
            borderColor: 'border-emerald-400/20',
            animate: false,
        },
        disconnected: {
            icon: WifiOff,
            text: 'Frånkopplad',
            color: 'text-red-400',
            bgColor: 'bg-red-400/10',
            borderColor: 'border-red-400/20',
            animate: false,
        },
        error: {
            icon: WifiOff,
            text: 'Anslutningsfel',
            color: 'text-red-400',
            bgColor: 'bg-red-400/10',
            borderColor: 'border-red-400/20',
            animate: false,
        },
    };

    const config = statusConfig[connectionState];
    const Icon = config.icon;

    return (
        <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${config.bgColor} border ${config.borderColor}`}
        >
            <Icon
                className={`w-4 h-4 ${config.color} ${config.animate ? 'animate-spin' : ''}`}
            />
            <span className={`text-sm ${config.color}`}>{config.text}</span>

            {(connectionState === 'disconnected' || connectionState === 'error') && (
                <button
                    onClick={() => checkConnection()}
                    className="ml-2 px-2 py-0.5 text-xs rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition-colors"
                >
                    Återanslut
                </button>
            )}
        </div>
    );
}
