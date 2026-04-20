import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CATEGORIES, type Category } from '../data/categories';

export default function CategoriesPage() {
  const [activeCategory, setActiveCategory] = useState<Category | null>(null);

  function closePanel() {
    setActiveCategory(null);
  }

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') closePanel();
    }
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  return (
    <div className="flex flex-1 min-h-0 overflow-hidden relative bg-gray-100">

      {/* ── LEFT SIDEBAR ── */}
      <aside className="w-56 bg-white border-r border-gray-200 flex flex-col shrink-0 overflow-y-auto">
        <nav className="p-3 flex flex-col gap-1 flex-1">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 pt-2 pb-1">Main</p>

          <Link to="/dashboard" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Dashboard
          </Link>

          {/* Categories — active */}
          <span className="flex items-center gap-3 px-3 py-2 rounded-lg bg-indigo-50 text-indigo-700 text-sm font-medium">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            Categories
          </span>

          <Link to="/products" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            Projects
          </Link>

          <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Tasks
            <span className="ml-auto bg-indigo-100 text-indigo-700 text-xs font-semibold px-1.5 py-0.5 rounded-full">4</span>
          </a>

          <Link to="/chat" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            Messages
          </Link>

          <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Analytics
          </a>

          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 pt-4 pb-1">Settings</p>

          <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Settings
          </a>

          <Link to="/login" className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-800 text-sm transition">
            <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Logout
          </Link>
        </nav>
      </aside>

      {/* ── MAIN CONTENT ── */}
      <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
        <div className="mb-5">
          <h1 className="text-lg font-semibold text-gray-800">Categories</h1>
          <p className="text-sm text-gray-500">Click a category card to view its details</p>
        </div>

        <div className="flex flex-nowrap gap-4 overflow-x-auto pb-2">
          {CATEGORIES.map((category) => (
            <div
              key={category.id}
              onClick={() => setActiveCategory(category)}
              className={`w-44 flex-shrink-0 bg-white rounded-xl border p-5 cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 ${
                activeCategory?.id === category.id
                  ? 'border-indigo-400 shadow-md'
                  : 'border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center text-lg"
                  style={{ backgroundColor: `${category.color}20` }}
                >
                  {category.icon}
                </div>
                <span
                  className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                    category.status === 'Active'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-500'
                  }`}
                >
                  {category.status}
                </span>
              </div>
              <h3 className="font-semibold text-gray-800 text-sm mb-1">{category.name}</h3>
              <p className="text-xs text-gray-500 mb-3 leading-relaxed line-clamp-2">{category.description}</p>
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: category.color }} />
                <span className="text-xs text-gray-400">{category.itemCount} items</span>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* ── OVERLAY ── */}
      <div
        onClick={closePanel}
        className={`absolute inset-0 bg-black/30 z-10 transition-opacity duration-300 ${
          activeCategory ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
      />

      {/* ── RIGHT DETAIL PANEL ── */}
      <aside
        className={`absolute top-0 right-0 h-full w-80 bg-white border-l border-gray-200 z-20 flex flex-col shadow-2xl transition-transform duration-300 ease-in-out ${
          activeCategory ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {activeCategory && (
          <>
            {/* Panel header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 shrink-0">
              <div className="flex items-center gap-3">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-base"
                  style={{ backgroundColor: `${activeCategory.color}20` }}
                >
                  {activeCategory.icon}
                </div>
                <div>
                  <h2 className="font-semibold text-gray-800 text-sm">{activeCategory.name}</h2>
                  <p className="text-xs text-gray-400">{activeCategory.itemCount} items</p>
                </div>
              </div>
              <button
                onClick={closePanel}
                className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Panel body */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="mb-5">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1.5">Description</p>
                <p className="text-sm text-gray-600 leading-relaxed">{activeCategory.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-5">
                <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                  <p className="text-xs text-gray-400 mb-1">Status</p>
                  <span
                    className={`text-sm font-semibold ${
                      activeCategory.status === 'Active' ? 'text-green-600' : 'text-gray-500'
                    }`}
                  >
                    {activeCategory.status}
                  </span>
                </div>
                <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                  <p className="text-xs text-gray-400 mb-1">Items</p>
                  <span className="text-sm font-semibold text-gray-700">{activeCategory.itemCount}</span>
                </div>
              </div>

              <div className="mb-5">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Colour</p>
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full border border-gray-200" style={{ backgroundColor: activeCategory.color }} />
                  <span className="text-sm text-gray-500 font-mono">{activeCategory.color}</span>
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Tags</p>
                <div className="flex flex-wrap gap-1.5">
                  {activeCategory.tags.map((tag) => (
                    <span key={tag} className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Panel footer */}
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end shrink-0 bg-gray-50">
              <button
                onClick={closePanel}
                className="px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-white transition font-medium"
              >
                Close
              </button>
            </div>
          </>
        )}
      </aside>
    </div>
  );
}
