'use client';

import { useState, useEffect, useMemo } from 'react';
import Layout from '@/components/Layout';
import MatchCard from '@/components/MatchCard';
import { MatchLink } from '@/types/api';
import { RefreshCw, Search, Filter, ChevronLeft, ChevronRight, Clock } from 'lucide-react';
import ApiService from '@/services/api';

export default function HomePage() {
  const [matches, setMatches] = useState<MatchLink[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);
  
  // Estados para filtros e paginação
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'text' | 'match_id'>('text');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12);

  // Carregar dados da API
  const loadLatestLinks = async (showLoading = false) => {
    if (showLoading) setIsLoading(true);
    setError(null);
    
    try {
      const response = await ApiService.getLatestLinks();
      
      if (response.success) {
        setMatches(response.data.filtered_links);
        setLastUpdate(response.collection_info.collection_timestamp);
      } else {
        setError(response.message || 'Erro ao carregar partidas');
      }
    } catch (err) {
      console.error('Erro ao carregar partidas:', err);
      setError('Erro de conexão com a API');
    } finally {
      setIsInitialLoading(false);
      if (showLoading) setIsLoading(false);
    }
  };

  useEffect(() => {
    loadLatestLinks();
  }, []);

  const handleRefresh = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const collectResponse = await ApiService.collectLinks();
      
      if (collectResponse.success) {
        await loadLatestLinks();
      } else {
        setError(collectResponse.message || 'Erro ao coletar novas partidas');
      }
    } catch (err) {
      console.error('Erro ao atualizar partidas:', err);
      setError('Erro ao coletar novas partidas');
    } finally {
      setIsLoading(false);
    }
  };

  // Filtrar e ordenar partidas
  const filteredAndSortedMatches = useMemo(() => {
    let filtered = matches.filter(match =>
      match.text.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Ordenação
    filtered.sort((a, b) => {
      if (sortBy === 'text') {
        return a.text.localeCompare(b.text);
      }
      return a.match_id.localeCompare(b.match_id);
    });

    return filtered;
  }, [matches, searchTerm, sortBy]);

  // Paginação
  const totalPages = Math.ceil(filteredAndSortedMatches.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedMatches = filteredAndSortedMatches.slice(startIndex, startIndex + itemsPerPage);

  // Reset página quando filtros mudam
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, sortBy]);

  // Função para formatar a data da última atualização
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

  if (isInitialLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Buscando partidas atualizadas</h3>
            <p className="text-gray-600">Coletando novos links do SofaScore...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header simples */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Partidas de Futebol</h1>
            <p className="text-gray-600">
              {filteredAndSortedMatches.length} partidas encontradas
            </p>
            {lastUpdate && (
              <div className="flex items-center mt-2 text-sm text-gray-500">
                <Clock className="h-4 w-4 mr-1" />
                <span>Última atualização: {formatLastUpdate(lastUpdate)}</span>
              </div>
            )}
          </div>
          
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            {isLoading ? 'Atualizando...' : 'Atualizar'}
          </button>
        </div>

        {/* Filtros e busca */}
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Busca */}
            <div className="flex-1">
              <div className="relative">
                <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar por times..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            
            {/* Ordenação */}
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'text' | 'match_id')}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="text">Ordenar por Times</option>
                <option value="match_id">Ordenar por ID</option>
              </select>
            </div>
          </div>
        </div>

        {/* Erro */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Lista de partidas */}
        {paginatedMatches.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {paginatedMatches.map((match, index) => (
                <MatchCard key={`${match.match_id}-${index}-${match.url}`} match={match} />
              ))}
            </div>

            {/* Paginação */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center space-x-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="flex items-center px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Anterior
                </button>
                
                <span className="px-4 py-2 text-sm text-gray-700">
                  Página {currentPage} de {totalPages}
                </span>
                
                <button
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className="flex items-center px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Próxima
                  <ChevronRight className="h-4 w-4 ml-1" />
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">
              {searchTerm ? 'Nenhuma partida encontrada com esse filtro.' : 'Nenhuma partida disponível.'}
            </p>
            {!searchTerm && (
              <button
                onClick={handleRefresh}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Buscar Partidas
              </button>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}
