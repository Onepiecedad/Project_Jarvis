import { ChatPanel } from '@/components/chat/ChatPanel';
import { DynamicViewPanel } from '@/components/views/DynamicViewPanel';
import { ConnectionStatus } from '@/components/ui/ConnectionStatus';
import { Bot, Menu, Settings, History, Users, FileText, BarChart3 } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex h-screen bg-slate-950 text-white">
      {/* Sidebar */}
      <aside className="w-16 flex flex-col items-center py-4 bg-slate-900 border-r border-slate-800">
        {/* Logo */}
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center mb-8 shadow-lg shadow-blue-500/20">
          <Bot className="w-5 h-5 text-white" />
        </div>

        {/* Nav Icons */}
        <nav className="flex-1 flex flex-col items-center gap-4">
          <NavIcon icon={History} label="Historik" active />
          <NavIcon icon={FileText} label="Tasks" />
          <NavIcon icon={Users} label="Entities" />
          <NavIcon icon={BarChart3} label="Analytics" />
        </nav>

        {/* Settings */}
        <NavIcon icon={Settings} label="Inställningar" />
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex">
        {/* Chat Panel - Left */}
        <div className="w-[400px] border-r border-slate-800 flex flex-col">
          <ChatPanel />
        </div>

        {/* Dynamic View Panel - Right */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <header className="flex items-center justify-between px-6 py-3 border-b border-slate-800 bg-slate-900/50">
            <div>
              <h1 className="text-lg font-semibold">JARVIS Dashboard</h1>
              <p className="text-sm text-slate-400">Skyland AI</p>
            </div>
            <ConnectionStatus />
          </header>

          {/* Content */}
          <div className="flex-1 overflow-hidden">
            <DynamicViewPanel />
          </div>
        </div>
      </main>
    </div>
  );
}

function NavIcon({
  icon: Icon,
  label,
  active = false
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  active?: boolean;
}) {
  return (
    <button
      title={label}
      className={`w-10 h-10 rounded-lg flex items-center justify-center transition-colors ${active
          ? 'bg-blue-500/20 text-blue-400'
          : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800'
        }`}
    >
      <Icon className="w-5 h-5" />
    </button>
  );
}
