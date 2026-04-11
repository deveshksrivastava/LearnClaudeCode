import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { PROJECTS } from '../data/projects';

export default function ProjectDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const project = PROJECTS.find((p) => p.slug === slug);

  const [checkedItems, setCheckedItems] = useState<boolean[]>(() => {
    if (!project) return [];
    const done = Math.round((project.progress / 100) * project.checklist.length);
    return project.checklist.map((_, i) => i < done);
  });

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <p className="text-gray-500 text-sm">Project not found.</p>
        <Link to="/dashboard" className="text-indigo-600 text-sm hover:underline">
          ← Back to Dashboard
        </Link>
      </div>
    );
  }

  const completedCount = checkedItems.filter(Boolean).length;

  function toggleCheck(index: number) {
    setCheckedItems((prev) => prev.map((v, i) => (i === index ? !v : v)));
  }

  return (
    <div className="flex flex-1 min-h-0 overflow-hidden bg-gray-50">
      {/* ── SIDEBAR ── */}
      <aside className="w-56 bg-white border-r border-gray-200 flex flex-col shrink-0 overflow-y-auto">
        <nav className="p-3 flex flex-col gap-1 flex-1">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 pt-2 pb-1">Main</p>

          <Link
            to="/dashboard"
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition"
          >
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Dashboard
          </Link>

          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 pt-4 pb-1">Projects</p>
          {PROJECTS.map((p) => (
            <Link
              key={p.slug}
              to={`/project/${p.slug}`}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition ${
                p.slug === slug
                  ? 'bg-indigo-50 text-indigo-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
              }`}
            >
              <span
                className="w-2 h-2 rounded-full shrink-0"
                style={{ backgroundColor: p.color }}
              />
              {p.title}
            </Link>
          ))}
        </nav>
      </aside>

      {/* ── MAIN CONTENT ── */}
      <main className="flex-1 overflow-y-auto p-6">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-xs text-gray-400 mb-4">
          <Link to="/dashboard" className="hover:text-indigo-600 transition">Dashboard</Link>
          <span>/</span>
          <span className="text-gray-600">{project.title}</span>
        </div>

        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-4">
            <div
              className={`w-12 h-12 ${project.iconBg} rounded-xl flex items-center justify-center`}
            >
              <span className={`${project.iconColor} w-6 h-6`}>
                {/* reuse first letter avatar as fallback icon */}
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V9l-6-6z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v6h6" />
                </svg>
              </span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">{project.title}</h1>
              <p className="text-sm text-gray-500">{project.category}</p>
            </div>
          </div>
          <span
            className={`text-xs ${project.statusBg} ${project.statusTextColor} font-semibold px-3 py-1 rounded-full`}
          >
            {project.status}
          </span>
        </div>

        {/* ── GRID LAYOUT ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

          {/* Left column — spans 2 */}
          <div className="lg:col-span-2 flex flex-col gap-5">

            {/* Description */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">About</p>
              <p className="text-sm text-gray-600 leading-relaxed">{project.fullDesc}</p>
            </div>

            {/* Progress */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Overall Progress</p>
                <span className="text-sm font-bold" style={{ color: project.color }}>{project.progress}%</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-3">
                <div
                  className="h-3 rounded-full transition-all duration-500"
                  style={{ width: `${project.progress}%`, backgroundColor: project.color }}
                />
              </div>
            </div>

            {/* Checklist */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Checklist</p>
                <span className="text-xs text-gray-500">{completedCount} / {project.checklist.length} done</span>
              </div>
              <div className="flex flex-col gap-2.5">
                {project.checklist.map((item, i) => (
                  <label key={i} className="flex items-center gap-3 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={checkedItems[i] ?? false}
                      onChange={() => toggleCheck(i)}
                      className="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-400 cursor-pointer"
                    />
                    <span
                      className={`text-sm transition group-hover:text-gray-800 ${
                        checkedItems[i] ? 'line-through text-gray-400' : 'text-gray-700'
                      }`}
                    >
                      {item}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Timeline */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Timeline</p>
              <ol className="relative border-l-2 border-gray-200 ml-2 flex flex-col gap-5">
                {project.timeline.map((entry, i) => (
                  <li key={i} className="ml-5 relative">
                    <span
                      className="absolute -left-[1.65rem] top-0.5 w-3 h-3 rounded-full border-2 border-white"
                      style={{ backgroundColor: project.color }}
                    />
                    <p className="text-xs text-gray-400 mb-0.5">{entry.date}</p>
                    <p className="text-sm text-gray-700">{entry.event}</p>
                  </li>
                ))}
              </ol>
            </div>
          </div>

          {/* Right column */}
          <div className="flex flex-col gap-5">

            {/* Stats */}
            <div className="bg-white rounded-xl border border-gray-200 p-5 grid grid-cols-2 gap-3">
              <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                <p className="text-xs text-gray-400 mb-1">Status</p>
                <p className="text-sm font-semibold text-gray-700">{project.status}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                <p className="text-xs text-gray-400 mb-1">Progress</p>
                <p className="text-sm font-semibold text-gray-700">{project.progress}%</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                <p className="text-xs text-gray-400 mb-1">Tasks</p>
                <p className="text-sm font-semibold text-gray-700">{project.checklist.length} items</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                <p className="text-xs text-gray-400 mb-1">Category</p>
                <p className="text-sm font-semibold text-gray-700 truncate">{project.category}</p>
              </div>
            </div>

            {/* Tech Stack */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Tech Stack</p>
              <div className="flex flex-wrap gap-2">
                {project.techStack.map((tech) => (
                  <span
                    key={tech}
                    className="text-xs font-medium px-2.5 py-1 rounded-full bg-gray-100 text-gray-600"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>

            {/* Team */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Team</p>
              <div className="flex flex-col gap-3">
                {project.team.map((member) => (
                  <div key={member.name} className="flex items-center gap-3">
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0"
                      style={{ backgroundColor: project.color }}
                    >
                      {member.avatar}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">{member.name}</p>
                      <p className="text-xs text-gray-400">{member.role}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Links */}
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Links</p>
              <div className="flex flex-col gap-2">
                {project.links.map((link) => (
                  <a
                    key={link.label}
                    href={link.url}
                    className="flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800 transition"
                  >
                    <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    {link.label}
                  </a>
                ))}
              </div>
            </div>

            {/* Back button */}
            <Link
              to="/dashboard"
              className="flex items-center justify-center gap-2 text-sm text-gray-500 border border-gray-200 rounded-xl py-2.5 hover:bg-white hover:text-gray-800 transition"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Dashboard
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
