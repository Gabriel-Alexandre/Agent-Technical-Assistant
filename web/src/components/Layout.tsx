import Link from 'next/link';
import { Activity, BarChart3, Home } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Activity className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-xl font-bold text-gray-900">
                Assistente Técnico de Futebol
              </h1>
            </div>
            
            <nav className="flex space-x-8">
              <Link 
                href="/" 
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-100 rounded-md transition-colors"
              >
                <Home className="h-4 w-4 mr-2" />
                Partidas ao Vivo
              </Link>
              <Link 
                href="/historico" 
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-100 rounded-md transition-colors"
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Histórico de Análises
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>© 2024 Assistente Técnico de Futebol - Análises em tempo real do SofaScore</p>
            <p className="mt-1">
              Powered by{' '}
              <span className="font-medium text-blue-600">FastAPI</span>
              {' '}+{' '}
              <span className="font-medium text-blue-600">Next.js</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
} 