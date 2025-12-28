'use client';

import { useChatStore } from '@/stores/chatStore';
import { DynamicView } from '@/types/jarvis';
import { Table, Layers, FileText, ChartBar, Inbox, Image, ExternalLink } from 'lucide-react';

export function DynamicViewPanel() {
    const { dynamicView } = useChatStore();

    if (!dynamicView) {
        return <EmptyView />;
    }

    return (
        <div className="h-full flex flex-col bg-slate-950">
            {/* Header */}
            {dynamicView.title && (
                <div className="px-6 py-4 border-b border-slate-800">
                    <h2 className="text-lg font-semibold text-white">{dynamicView.title}</h2>
                    {dynamicView.subtitle && (
                        <p className="text-sm text-slate-400 mt-1">{dynamicView.subtitle}</p>
                    )}
                </div>
            )}

            {/* Content */}
            <div className="flex-1 overflow-auto p-6">
                {dynamicView.type === 'table' && <TableView data={dynamicView.data} />}
                {dynamicView.type === 'card' && <CardView data={dynamicView.data} />}
                {dynamicView.type === 'list' && <ListView data={dynamicView.data} />}
                {dynamicView.type === 'gallery' && <GalleryView data={dynamicView.data} />}
                {dynamicView.type === 'empty' && <EmptyView />}
            </div>
        </div>
    );
}

function EmptyView() {
    return (
        <div className="h-full flex flex-col items-center justify-center text-slate-500">
            <div className="w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center mb-4">
                <Layers className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-medium text-slate-400">Ingen vy vald</h3>
            <p className="text-sm text-slate-500 mt-1">
                Be JARVIS visa något för att se det här
            </p>
        </div>
    );
}

function TableView({ data }: { data: unknown }) {
    if (!Array.isArray(data) || data.length === 0) {
        return <EmptyDataMessage />;
    }

    const columns = Object.keys(data[0]);

    return (
        <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full">
                <thead>
                    <tr className="bg-slate-800/50">
                        {columns.map((col) => (
                            <th
                                key={col}
                                className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider"
                            >
                                {col}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                    {data.map((row, idx) => (
                        <tr
                            key={idx}
                            className="hover:bg-slate-800/30 transition-colors"
                        >
                            {columns.map((col) => (
                                <td key={col} className="px-4 py-3 text-sm text-slate-300">
                                    {formatCellValue((row as Record<string, unknown>)[col])}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

function CardView({ data }: { data: unknown }) {
    if (!Array.isArray(data) || data.length === 0) {
        return <EmptyDataMessage />;
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.map((item, idx) => (
                <div
                    key={idx}
                    className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-slate-600/50 transition-colors"
                >
                    {Object.entries(item as Record<string, unknown>).map(([key, value]) => (
                        <div key={key} className="mb-2 last:mb-0">
                            <span className="text-xs text-slate-500 uppercase">{key}</span>
                            <p className="text-sm text-slate-200">{formatCellValue(value)}</p>
                        </div>
                    ))}
                </div>
            ))}
        </div>
    );
}

function ListView({ data }: { data: unknown }) {
    if (!Array.isArray(data) || data.length === 0) {
        return <EmptyDataMessage />;
    }

    return (
        <ul className="space-y-2">
            {data.map((item, idx) => (
                <li
                    key={idx}
                    className="px-4 py-3 rounded-lg bg-slate-800/30 border border-slate-700/30 text-slate-300"
                >
                    {typeof item === 'object' ? JSON.stringify(item) : String(item)}
                </li>
            ))}
        </ul>
    );
}

interface MediaItem {
    url: string;
    alt?: string;
    title?: string;
    type?: string;
}

function GalleryView({ data }: { data: unknown }) {
    if (!Array.isArray(data) || data.length === 0) {
        return <EmptyDataMessage message="Inga bilder hittades" />;
    }

    return (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {data.map((item, idx) => {
                const media = item as MediaItem;
                const isVideo = media.type === 'video' || media.url?.includes('video') || media.url?.endsWith('.mp4');

                return (
                    <div
                        key={idx}
                        className="group relative aspect-square rounded-xl overflow-hidden bg-slate-800 border border-slate-700/50 hover:border-blue-500/50 transition-all"
                    >
                        {isVideo ? (
                            <video
                                src={media.url}
                                className="w-full h-full object-cover"
                                controls={false}
                                muted
                            />
                        ) : (
                            <img
                                src={media.url}
                                alt={media.alt || media.title || `Media ${idx + 1}`}
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                onError={(e) => {
                                    (e.target as HTMLImageElement).src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect fill="%23334155" width="100" height="100"/><text fill="%2394a3b8" x="50" y="55" text-anchor="middle" font-size="12">No Image</text></svg>';
                                }}
                            />
                        )}

                        {/* Overlay */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                            <div className="absolute bottom-0 left-0 right-0 p-3">
                                {media.title && (
                                    <p className="text-sm font-medium text-white truncate">{media.title}</p>
                                )}
                                {media.alt && media.alt !== media.title && (
                                    <p className="text-xs text-slate-300 truncate">{media.alt}</p>
                                )}
                            </div>

                            {/* Open in new tab */}
                            <a
                                href={media.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                title="Öppna i ny flik"
                                className="absolute top-2 right-2 p-2 rounded-lg bg-black/50 hover:bg-black/70 transition-colors"
                            >
                                <ExternalLink className="w-4 h-4 text-white" />
                            </a>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

function EmptyDataMessage({ message = "Ingen data att visa" }: { message?: string }) {
    return (
        <div className="flex flex-col items-center justify-center py-12 text-slate-500">
            <Inbox className="w-12 h-12 mb-3" />
            <p>{message}</p>
        </div>
    );
}

function formatCellValue(value: unknown): string {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'boolean') return value ? 'Ja' : 'Nej';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
}
