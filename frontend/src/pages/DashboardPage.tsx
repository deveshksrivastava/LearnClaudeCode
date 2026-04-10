import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

// ── Types ────────────────────────────────────────────────────────────────────

interface Project {
  title: string;
  category: string;
  color: string;
  iconBg: string;
  iconColor: string;
  borderHover: string;
  shortDesc: string;
  fullDesc: string;
  status: string;
  statusBg: string;
  statusTextColor: string;
  progress: number;
  checklist: string[];
  icon: React.ReactNode;
}

// ── Project data ─────────────────────────────────────────────────────────────

const PROJECTS: Project[] = [
  {
    title: 'RAG Pipeline',
    category: 'Core AI Engineering',
    color: '#6366f1',
    iconBg: 'bg-indigo-100',
    iconColor: 'text-indigo-600',
    borderHover: 'hover:border-indigo-300',
    shortDesc: 'Build a production-grade RAG chatbot over real energy documents.',
    fullDesc: 'Build a production-grade RAG chatbot over real energy documents. Implement chunking, embedding, and retrieval strategies.',
    status: 'In Progress',
    statusBg: 'bg-yellow-100',
    statusTextColor: 'text-yellow-700',
    progress: 65,
    checklist: ['Set up ChromaDB vector store', 'Implement chunking strategy', 'Test retrieval accuracy', 'Connect to FastAPI backend', 'Write RAGAS evaluation'],
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V9l-6-6z"/>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v6h6"/>
      </svg>
    ),
  },
  {
    title: 'LangGraph Agent',
    category: 'Core AI Engineering',
    color: '#10b981',
    iconBg: 'bg-emerald-100',
    iconColor: 'text-emerald-600',
    borderHover: 'hover:border-emerald-300',
    shortDesc: 'Build a stateful multi-step agent with tool use and real API calls.',
    fullDesc: 'Build a stateful multi-step agent using LangGraph with tool use — web search, calculator, and real API calls.',
    status: 'Not Started',
    statusBg: 'bg-gray-100',
    statusTextColor: 'text-gray-600',
    progress: 0,
    checklist: ['Define agent state schema', 'Add web search tool', 'Add calculator tool', 'Build conversation memory', 'Test with real queries'],
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z"/>
      </svg>
    ),
  },
  {
    title: 'Azure Deployment',
    category: 'Production Systems',
    color: '#0ea5e9',
    iconBg: 'bg-sky-100',
    iconColor: 'text-sky-600',
    borderHover: 'hover:border-sky-300',
    shortDesc: 'Deploy to Azure Container Apps with full CI/CD pipeline.',
    fullDesc: 'Deploy the chatbot to Azure Container Apps with full GitHub Actions CI/CD pipeline across dev, UAT, and production environments.',
    status: 'Planned',
    statusBg: 'bg-blue-100',
    statusTextColor: 'text-blue-700',
    progress: 10,
    checklist: ['Set up Azure Container Apps', 'Write Bicep IaC templates', 'Configure GitHub Actions workflow', 'Add environment secrets', 'Test dev → UAT → prod flow'],
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"/>
      </svg>
    ),
  },
  {
    title: 'LangSmith Tracing',
    category: 'Observability',
    color: '#f97316',
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-600',
    borderHover: 'hover:border-orange-300',
    shortDesc: 'Set up observability — latency, token usage, cost per query.',
    fullDesc: 'Set up LangSmith observability across all AI pipeline stages. Track latency, token usage, failure rates, and cost per query.',
    status: 'In Progress',
    statusBg: 'bg-yellow-100',
    statusTextColor: 'text-yellow-700',
    progress: 40,
    checklist: ['Install LangSmith SDK', 'Add tracing to all chains', 'Set up project dashboard', 'Configure cost tracking', 'Create alert rules'],
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
      </svg>
    ),
  },
  {
    title: 'RAGAS Evaluation',
    category: 'Testing & Quality',
    color: '#ec4899',
    iconBg: 'bg-pink-100',
    iconColor: 'text-pink-600',
    borderHover: 'hover:border-pink-300',
    shortDesc: 'Faithfulness, relevancy, context precision metrics dashboard.',
    fullDesc: 'Implement RAGAS evaluation metrics — faithfulness, answer relevancy, context precision. Build a dashboard to track quality over time.',
    status: 'Completed',
    statusBg: 'bg-green-100',
    statusTextColor: 'text-green-700',
    progress: 100,
    checklist: ['Install RAGAS library', 'Define evaluation dataset', 'Run faithfulness metrics', 'Run relevancy metrics', 'Build reporting dashboard'],
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
    ),
  },
  {
    title: 'Multi-Agent System',
    category: 'AI Architecture',
    color: '#8b5cf6',
    iconBg: 'bg-violet-100',
    iconColor: 'text-violet-600',
    borderHover: 'hover:border-violet-300',
    shortDesc: 'Orchestrator + specialised sub-agents for energy domain queries.',
    fullDesc: 'Design and build a multi-agent system with an orchestrator directing specialised sub-agents for energy data queries and anomaly detection.',
    status: 'Planned',
    statusBg: 'bg-blue-100',
    statusTextColor: 'text-blue-700',
    progress: 5,
    checklist: ['Design agent architecture', 'Build orchestrator agent', 'Build energy query agent', 'Build anomaly detection agent', 'Test handoff between agents'],
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
      </svg>
    ),
  },
];

// ── Component ─────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [checkedItems, setCheckedItems] = useState<boolean[]>([]);
  const [notes, setNotes] = useState('');

  function openPanel(project: Project) {
    const done = Math.round((project.progress / 100) * project.checklist.length);
    setCheckedItems(project.checklist.map((_, i) => i < done));
    setNotes('');
    setActiveProject(project);
  }

  function closePanel() {
    setActiveProject(null);
  }

  function toggleCheck(index: number) {
    setCheckedItems((prev) => prev.map((v, i) => (i === index ? !v : v)));
  }

  // Close panel on Escape — useEffect so the listener is always active,
  // not just when a focusable element inside the div happens to be focused.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') closePanel();
    }
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  return (
    // flex-1 fills the space below the sticky NavBar; min-h-0 is required so
    // a flex child with overflow-hidden actually clips its overflow instead of
    // expanding to fit its content (flex's default min-height is "auto").
    <div className="flex flex-1 min-h-0 overflow-hidden relative bg-gray-100">
      {/* ── LEFT SIDEBAR ── */}
      <aside className="w-56 bg-white border-r border-gray-200 flex flex-col shrink-0 overflow-y-auto">
        <nav className="p-3 flex flex-col gap-1 flex-1">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 pt-2 pb-1">Main</p>

          {/* Dashboard — active */}
          <span className="flex items-center gap-3 px-3 py-2 rounded-lg bg-indigo-50 text-indigo-700 text-sm font-medium">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
            Dashboard
          </span>

          <Link to="/products" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
            </svg>
            Projects
          </Link>

          <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
            </svg>
            Tasks
            <span className="ml-auto bg-indigo-100 text-indigo-700 text-xs font-semibold px-1.5 py-0.5 rounded-full">4</span>
          </a>

          <Link to="/chat" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
            Messages
          </Link>

          <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
            Analytics
          </a>

          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 pt-4 pb-1">Settings</p>

          <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            Settings
          </a>

          <Link to="/login" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
            Logout
          </Link>
        </nav>
      </aside>

      {/* ── MAIN CONTENT ── */}
      <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
        <div className="mb-5 ">
          <h1 className="text-lg font-semibold text-gray-800">Dashboard</h1>
          <p className="text-sm text-gray-500">Click any card to view details</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {PROJECTS.map((project) => (
            <div
              key={project.title}
              onClick={() => openPanel(project)}
              className={`bg-white rounded-xl border border-gray-200 p-5 cursor-pointer hover:shadow-md hover:-translate-y-0.5 ${project.borderHover} transition-all duration-200`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`w-9 h-9 ${project.iconBg} rounded-lg flex items-center justify-center`}>
                  <span className={project.iconColor}>{project.icon}</span>
                </div>
                <span className={`text-xs ${project.statusBg} ${project.statusTextColor} font-medium px-2 py-0.5 rounded-full`}>
                  {project.status}
                </span>
              </div>
              <h3 className="font-semibold text-gray-800 text-sm mb-1">{project.title}</h3>
              <p className="text-xs text-gray-500 mb-3 leading-relaxed">{project.shortDesc}</p>
              <div className="w-full bg-gray-100 rounded-full h-1.5">
                <div
                  className="h-1.5 rounded-full"
                  style={{ width: `${project.progress}%`, backgroundColor: project.color }}
                />
              </div>
              <p className="text-xs text-gray-400 mt-1.5">{project.progress}% complete</p>
            </div>
          ))}
        </div>
      </main>

      {/* ── OVERLAY ── */}
      <div
        onClick={closePanel}
        className={`absolute inset-0 bg-black/30 z-10 transition-opacity duration-300 ${
          activeProject ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
      />

      {/* ── SLIDE PANEL ── */}
      <aside
        className={`absolute top-0 right-0 h-full w-1/2 bg-white border-l border-gray-200 z-20 flex flex-col shadow-2xl transition-transform duration-300 ease-in-out ${
          activeProject ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {activeProject && (
          <>
            {/* Panel header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: activeProject.color }} />
                <div>
                  <h2 className="font-semibold text-gray-800 text-sm">{activeProject.title}</h2>
                  <p className="text-xs text-gray-400">{activeProject.category}</p>
                </div>
              </div>
              <button
                onClick={closePanel}
                className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>

            {/* Panel body */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="mb-5">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1.5">Description</p>
                <p className="text-sm text-gray-600 leading-relaxed">{activeProject.fullDesc}</p>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-5">
                <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                  <p className="text-xs text-gray-400 mb-1">Status</p>
                  <span className="text-sm font-semibold text-gray-700">{activeProject.status}</span>
                </div>
                <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                  <p className="text-xs text-gray-400 mb-1">Progress</p>
                  <span className="text-sm font-semibold text-gray-700">{activeProject.progress}%</span>
                </div>
              </div>

              <div className="mb-5">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Progress Bar</p>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className="h-2 rounded-full transition-all duration-500"
                    style={{ width: `${activeProject.progress}%`, backgroundColor: activeProject.color }}
                  />
                </div>
              </div>

              <div className="mb-5">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Checklist</p>
                <div className="flex flex-col gap-2">
                  {activeProject.checklist.map((item, i) => (
                    <label key={i} className="flex items-center gap-2.5 cursor-pointer group">
                      <input
                        type="checkbox"
                        checked={checkedItems[i] ?? false}
                        onChange={() => toggleCheck(i)}
                        className="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-400 cursor-pointer"
                      />
                      <span className={`text-sm transition group-hover:text-gray-800 ${checkedItems[i] ? 'line-through text-gray-400' : 'text-gray-600'}`}>
                        {item}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Notes</p>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add your notes here..."
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl p-3 text-sm text-gray-600 resize-none h-24 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-transparent transition"
                />
              </div>
            </div>

            {/* Panel footer */}
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between shrink-0 bg-gray-50">
              <button className="text-sm text-gray-500 hover:text-gray-700 transition font-medium">
                Mark Complete
              </button>
              <div className="flex gap-2">
                <button
                  onClick={closePanel}
                  className="px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-white transition font-medium"
                >
                  Close
                </button>
                <button className="px-4 py-2 text-sm text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition font-medium">
                  Save Changes
                </button>
              </div>
            </div>
          </>
        )}
      </aside>
    </div>
  );
}
