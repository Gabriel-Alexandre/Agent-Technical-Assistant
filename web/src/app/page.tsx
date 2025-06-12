'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import MatchCard from '@/components/MatchCard';
import { MatchLink } from '@/types/api';
import { RefreshCw, Clock } from 'lucide-react';
import ApiService from '@/services/api';

export default function HomePage() {
  const [matches, setMatches] = useState<MatchLink[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);

  // Carregar dados da API
  const loadLatestLinks = async () => {
    try {
      const response = await ApiService.getLatestLinks();
      
      if (response.success) {
        setMatches(response.data.filtered_links);
        setLastUpdate(response.collection_info.collection_timestamp);
      }
    } catch (err) {
      console.error('Erro ao carregar links:', err);
    } finally {
      setIsInitialLoading(false);
    }
  };

  // Carregamento inicial
  useEffect(() => {
    loadLatestLinks();
  }, []);

  const handleRefresh = async () => {
    setIsLoading(true);
    
    try {
      // Chama a rota POST para coletar novos links
      await ApiService.collectLinks();
      // Após terminar, faz refresh da página para pegar a versão mais recente
      window.location.reload();
    } catch (err) {
      console.error('Erro ao atualizar links:', err);
      setIsLoading(false);
    }
  };

  const formatLastUpdate = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return 'Data indisponível';
    }
  };

  // Loading inicial no centro da tela
  if (isInitialLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full min-h-[50vh]">
          <div className="text-center">
            <RefreshCw className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Carregando partidas</h3>
            <p className="text-gray-600">Buscando os links mais recentes...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header da página */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Partidas Recentes</h1>
            <p className="text-gray-600 mt-1">
              Links mais recentes coletados do SofaScore
            </p>
            {lastUpdate && (
              <div className="flex items-center mt-2 text-sm text-gray-500">
                <Clock className="h-4 w-4 mr-1" />
                <span>Última atualização: {formatLastUpdate(lastUpdate)}</span>
              </div>
            )}
          </div>
          
          {/* Botão de atualizar */}
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            {isLoading ? 'Atualizando...' : 'Atualizar'}
          </button>
        </div>

        {/* Loading state durante atualização */}
        {isLoading && matches.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center">
              <RefreshCw className="h-5 w-5 animate-spin text-blue-600 mr-3" />
              <span className="text-blue-800">Coletando novos links...</span>
            </div>
          </div>
        )}

        {/* Lista de partidas */}
        {matches.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {matches.map((match) => (
              <MatchCard
                key={match.match_id}
                match={match}
              />
            ))}
          </div>
        )}

        {/* Estado vazio */}
        {!isLoading && matches.length === 0 && (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhuma partida encontrada
            </h3>
            <p className="text-gray-600 mb-4">
              Clique em "Atualizar" para coletar novos links.
            </p>
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Atualizar
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
