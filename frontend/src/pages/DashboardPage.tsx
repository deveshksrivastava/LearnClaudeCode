import { useState } from 'react';

const sidebarItems = [
  { icon: '🏠', label: 'Home' },
  { icon: '📦', label: 'Products' },
  { icon: '🛒', label: 'Orders' },
  { icon: '👥', label: 'Customers' },
  { icon: '📊', label: 'Analytics' },
  { icon: '⚙️', label: 'Settings' },
];

const topMenuItems = ['Overview', 'Sales', 'Revenue', 'Traffic', 'Reports'];

const cards = [
  { title: 'Total Sales', value: '$12,450', change: '+8.2%', positive: true, icon: '💰' },
  { title: 'New Orders', value: '342', change: '+5.1%', positive: true, icon: '🛒' },
  { title: 'Active Users', value: '1,289', change: '-2.4%', positive: false, icon: '👥' },
  { title: 'Conversion Rate', value: '3.6%', change: '+0.9%', positive: true, icon: '📈' },
  { title: 'Avg. Order Value', value: '$36.40', change: '+1.7%', positive: true, icon: '🧾' },
  { title: 'Refunds', value: '14', change: '-3 today', positive: false, icon: '↩️' },
];

export default function DashboardPage() {
  const [activeNav, setActiveNav] = useState('Overview');
  const [activeSidebar, setActiveSidebar] = useState('Home');

  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">
      {/* Left Sidebar */}
      <aside className="w-60 bg-gray-900 text-white flex flex-col shrink-0">
        <div className="px-6 py-5 border-b border-gray-700">
          <span className="text-xl font-bold tracking-tight">ShopAdmin</span>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {sidebarItems.map((item) => (
            <button
              key={item.label}
              onClick={() => setActiveSidebar(item.label)}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeSidebar === item.label
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-sm font-bold">
              A
            </div>
            <div className="text-sm">
              <p className="font-medium">Admin</p>
              <p className="text-gray-400 text-xs">admin@shop.com</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Menu Bar */}
        <header className="bg-white border-b border-gray-200 px-6 py-0 shrink-0">
          <div className="flex items-center justify-between h-14">
            <nav className="flex gap-1">
              {topMenuItems.map((item) => (
                <button
                  key={item}
                  onClick={() => setActiveNav(item)}
                  className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    activeNav === item
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-500 hover:text-gray-800 hover:bg-gray-100'
                  }`}
                >
                  {item}
                </button>
              ))}
            </nav>
            <div className="flex items-center gap-3">
              <button className="text-gray-400 hover:text-gray-700 text-xl">🔔</button>
              <button className="text-gray-400 hover:text-gray-700 text-xl">🔍</button>
            </div>
          </div>
        </header>

        {/* Cards Area */}
        <main className="flex-1 overflow-y-auto p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-6">{activeNav}</h1>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {cards.map((card) => (
              <div
                key={card.title}
                className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-gray-500 text-sm font-medium">{card.title}</span>
                  <span className="text-2xl">{card.icon}</span>
                </div>
                <p className="text-3xl font-bold text-gray-800">{card.value}</p>
                <span
                  className={`inline-block mt-2 text-xs font-semibold px-2 py-0.5 rounded-full ${
                    card.positive
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-600'
                  }`}
                >
                  {card.change}
                </span>
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
