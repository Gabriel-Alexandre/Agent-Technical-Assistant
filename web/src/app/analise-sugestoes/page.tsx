'use client';

import { useSearchParams } from 'next/navigation';
import Layout from '@/components/Layout';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function AnalyseSugestoesPage() {
  const searchParams = useSearchParams();
  const href = searchParams.get('href');

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header da página */}
        <div className="flex items-center space-x-4">
          <Link 
            href="/"
            className="flex items-center px-3 py-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Análise de Sugestões</h1>
            <p className="text-gray-600 mt-1">
              Análise detalhada da partida selecionada
            </p>
          </div>
        </div>

        {/* Informações da partida */}
        {href && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Partida Selecionada</h3>
            <div className="bg-gray-50 rounded-md p-4">
              <p className="text-sm text-gray-600 mb-2">Link original:</p>
              <code className="text-sm bg-gray-100 px-2 py-1 rounded">{href}</code>
            </div>
          </div>
        )}

        {/* Placeholder para análise */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Análise em Desenvolvimento</h3>
          <p className="text-gray-600">
            Esta página será implementada com as funcionalidades de análise de sugestões.
          </p>
        </div>
      </div>
    </Layout>
  );
} 