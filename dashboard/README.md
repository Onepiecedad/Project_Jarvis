# JARVIS Dashboard

AI-powered dashboard for Skyland AI - Phase 2 of the JARVIS project.

## Features

- 💬 **Real-time Chat** - WebSocket connection to JARVIS (Agent Zero)
- 📊 **Dynamic Views** - Tables, cards, and lists rendered on JARVIS command
- ✅ **Task Management** - View and manage tasks from Supabase
- 👥 **Entity Browser** - Browse companies, persons, and projects
- 🔐 **Authentication** - Supabase Auth integration

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS v4
- **State Management**: Zustand
- **Database**: Supabase (PostgreSQL + pgvector)
- **Real-time**: WebSocket (Agent Zero)
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+
- JARVIS (Agent Zero) running on `localhost:50080`
- Supabase project configured

### Installation

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Edit .env.local with your credentials
```

### Environment Variables

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_JARVIS_WS_URL=ws://localhost:50080/ws
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
npm start
```

## Project Structure

```
dashboard/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── layout.tsx
│   │   ├── page.tsx        # Main dashboard
│   │   └── globals.css
│   ├── components/
│   │   ├── chat/           # Chat interface
│   │   │   └── ChatPanel.tsx
│   │   ├── views/          # Dynamic view renderers
│   │   │   └── DynamicViewPanel.tsx
│   │   └── ui/             # Reusable UI components
│   │       └── ConnectionStatus.tsx
│   ├── hooks/
│   │   └── useJarvisSocket.ts  # WebSocket connection
│   ├── lib/
│   │   └── supabase.ts     # Supabase client & types
│   ├── stores/
│   │   └── chatStore.ts    # Zustand state store
│   └── types/
│       └── jarvis.ts       # TypeScript types
└── package.json
```

## WebSocket Protocol

### Dashboard → JARVIS

```json
{
  "type": "user_message",
  "content": "Visa alla tasks",
  "context": { "source": "dashboard" }
}
```

### JARVIS → Dashboard

```json
{
  "type": "render",
  "component": "table",
  "data": [...],
  "message": "Hittade 5 tasks"
}
```

## Roadmap

- [x] Basic chat interface
- [x] Connection status indicator
- [x] Dynamic view rendering (table, card, list)
- [ ] Authentication with Supabase Auth
- [ ] Task management page
- [ ] Entity browser page
- [ ] Voice input (optional)
- [ ] Dark/light theme toggle

## License

MIT
