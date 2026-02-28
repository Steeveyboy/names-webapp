import { Link, Outlet, useLocation } from 'react-router-dom';
import { BarChart3, Search, BookOpen, Lightbulb } from 'lucide-react';

const navLinks = [
  { to: '/', label: 'Analyze', icon: Search },
  { to: '/facts', label: 'Facts', icon: Lightbulb },
  { to: '/etymology', label: 'Etymology', icon: BookOpen },
] as const;

export function Layout() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header / Nav */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2">
              <BarChart3 className="w-8 h-8 text-indigo-600" />
              <span className="text-xl font-semibold text-indigo-600">Nomi</span>
            </Link>
            <nav className="flex items-center gap-1">
              {navLinks.map(({ to, label, icon: Icon }) => (
                <Link
                  key={to}
                  to={to}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === to
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Page Content */}
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <Outlet />
      </main>
    </div>
  );
}
