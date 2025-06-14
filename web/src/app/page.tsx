'use client';

import { useState, useEffect, useMemo } from 'react';
import Layout from '@/components/Layout';
import MatchCard from '@/components/MatchCard';
import { DetailedMatch } from '@/types/api';
import { RefreshCw, Search, Filter, ChevronLeft, ChevronRight, Clock, Play, Square, CheckCircle } from 'lucide-react';
import ApiService from '@/services/api';

export default function HomePage() {
  const [matches, setMatches] = useState<DetailedMatch[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);
  const [totalMatches, setTotalMatches] = useState(0);
  const [updateSuccess, setUpdateSuccess] = useState(false);
  
  // Estados para filtros e paginação
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'teams' | 'status' | 'time'>('status');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12);

  // Carregar dados da API
  const loadMatches = async () => {
    setIsInitialLoading(true);
    setError(null);
    
    try {
      console.log("📋 Carregando dados salvos mais recentes...");
      const latestResponse = await ApiService.getLatestLinks();
      
      if (latestResponse.success && latestResponse.data.filtered_links.length > 0) {
        // IMPORTANTE: A rota GET retorna os campos home_team e away_team invertidos
        // Precisamos corrigir isso para manter a consistência
        const correctedMatches = latestResponse.data.filtered_links.map(match => ({
          ...match,
          home_team: match.away_team, // Corrigindo a inversão
          away_team: match.home_team, // Corrigindo a inversão
          home_score: match.away_score, // Corrigindo a inversão
          away_score: match.home_score  // Corrigindo a inversão
        }));
        
        setMatches(correctedMatches);
        setLastUpdate(latestResponse.collection_info.collection_timestamp);
        setTotalMatches(latestResponse.data.statistics.total_filtered_links);
        console.log(`✅ Dados carregados: ${latestResponse.data.statistics.total_filtered_links} partidas`);
      } else {
        // Se não há dados salvos, fazer coleta nova automaticamente
        console.log("📋 Nenhum dado salvo, fazendo coleta inicial...");
        const response = await ApiService.collectDetailedLinks();
        
        if (response.success) {
          // A rota POST já retorna os dados no formato correto
          setMatches(response.data.detailed_matches);
          setLastUpdate(response.data.collected_at);
          setTotalMatches(response.data.total_detailed_matches);
          console.log(`✅ Coleta inicial concluída: ${response.data.total_detailed_matches} partidas`);
        } else {
          setError(response.message || 'Erro ao carregar partidas');
        }
      }
    } catch (err) {
      console.error('❌ Erro ao carregar partidas:', err);
      setError('Erro de conexão com a API. Verifique se o servidor está rodando.');
    } finally {
      setIsInitialLoading(false);
    }
  };

  useEffect(() => {
    loadMatches(); // Carregamento inicial usa GET
  }, []);

  // Limpar mensagem de sucesso após 3 segundos
  useEffect(() => {
    if (updateSuccess) {
      const timer = setTimeout(() => {
        setUpdateSuccess(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [updateSuccess]);

  const handleRefresh = async () => {
    setIsLoading(true);
    setError(null);
    setUpdateSuccess(false);
    
    try {
      console.log("🔄 Iniciando atualização manual...");
      console.log("⏳ Esta operação pode levar até 2 minutos...");
      
      const response = await ApiService.collectDetailedLinks();
      
      if (response.success) {
        // A rota POST já retorna os dados no formato correto
        setMatches(response.data.detailed_matches);
        setLastUpdate(response.data.collected_at);
        setTotalMatches(response.data.total_detailed_matches);
        console.log(`✅ Atualização concluída: ${response.data.total_detailed_matches} partidas`);
        setUpdateSuccess(true);
      } else {
        setError(response.message || 'Erro ao coletar novas partidas');
        console.error("❌ Erro na resposta da API:", response.message);
      }
    } catch (err: any) {
      console.error('❌ Erro ao atualizar partidas:', err);
      
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        setError('Timeout na coleta de dados. O servidor pode estar sobrecarregado. Tente novamente em alguns minutos.');
      } else if (err.code === 'ECONNREFUSED') {
        setError('Não foi possível conectar com a API. Verifique se o servidor está rodando.');
      } else {
        setError('Erro inesperado durante a atualização. Tente novamente.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Filtrar e ordenar partidas
  const filteredAndSortedMatches = useMemo(() => {
    let filtered = matches.filter(match => {
      const searchMatch = searchTerm === '' || 
        match.home_team.toLowerCase().includes(searchTerm.toLowerCase()) ||
        match.away_team.toLowerCase().includes(searchTerm.toLowerCase());
      
      const statusMatch = statusFilter === 'all' || match.match_status === statusFilter;
      
      return searchMatch && statusMatch;
    });

    // Ordenação
    filtered.sort((a, b) => {
      if (sortBy === 'teams') {
        return a.home_team.localeCompare(b.home_team);
      }
      
      if (sortBy === 'status') {
        const statusOrder = { 'in_progress': 0, 'not_started': 1, 'finished': 2, 'postponed': 3 };
        return statusOrder[a.match_status] - statusOrder[b.match_status];
      }
      
      if (sortBy === 'time') {
        // Para partidas em andamento, ordena por tempo de jogo
        if (a.match_status === 'in_progress' && b.match_status === 'in_progress') {
          const timeA = parseInt(a.match_time.replace(/[^\d]/g, '')) || 0;
          const timeB = parseInt(b.match_time.replace(/[^\d]/g, '')) || 0;
          return timeB - timeA; // Maior tempo primeiro
        }
        
        // Para outras, ordena por horário
        return a.match_time.localeCompare(b.match_time);
      }
      
      return 0;
    });

    return filtered;
  }, [matches, searchTerm, statusFilter, sortBy]);

  // Paginação
  const totalPages = Math.ceil(filteredAndSortedMatches.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedMatches = filteredAndSortedMatches.slice(startIndex, startIndex + itemsPerPage);

  // Reset página quando filtros mudam
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, statusFilter, sortBy]);

  // Função para formatar a data da última atualização
  const formatLastUpdate = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Data indisponível';
    }
  };

  // Contadores por status
  const statusCounts = useMemo(() => {
    return matches.reduce((acc, match) => {
      acc[match.match_status] = (acc[match.match_status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  }, [matches]);

  if (isInitialLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Buscando partidas de futebol</h3>
            <p className="text-gray-600">Coletando dados atualizados do SofaScore...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Partidas de Futebol Ao Vivo</h1>
            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
              <span>{filteredAndSortedMatches.length} de {totalMatches} partidas</span>
              {lastUpdate && (
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-1" />
                  <span>Atualizado: {formatLastUpdate(lastUpdate)}</span>
                </div>
              )}
            </div>
          </div>
          
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            {isLoading ? (
              <span className="flex flex-col items-start">
                <span>Coletando dados...</span>
                <span className="text-xs opacity-75">Pode levar até 2 min</span>
              </span>
            ) : 'Atualizar'}
          </button>
        </div>

        {/* Contadores de Status */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
            <Play className="h-5 w-5 text-green-600 mx-auto mb-1" />
            <div className="text-lg font-semibold text-green-800">{statusCounts.in_progress || 0}</div>
            <div className="text-xs text-green-700">Ao Vivo</div>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
            <Clock className="h-5 w-5 text-blue-600 mx-auto mb-1" />
            <div className="text-lg font-semibold text-blue-800">{statusCounts.not_started || 0}</div>
            <div className="text-xs text-blue-700">Não Iniciado</div>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-center">
            <CheckCircle className="h-5 w-5 text-gray-600 mx-auto mb-1" />
            <div className="text-lg font-semibold text-gray-800">{statusCounts.finished || 0}</div>
            <div className="text-xs text-gray-700">Finalizado</div>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-center">
            <Square className="h-5 w-5 text-yellow-600 mx-auto mb-1" />
            <div className="text-lg font-semibold text-yellow-800">{statusCounts.postponed || 0}</div>
            <div className="text-xs text-yellow-700">Adiado</div>
          </div>
        </div>

        {/* Filtros */}
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
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800"
                />
              </div>
            </div>
            
            {/* Filtro de Status */}
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800"
              >
                <option value="all">Todos os Status</option>
                <option value="in_progress">Ao Vivo</option>
                <option value="not_started">Não Iniciado</option>
                <option value="finished">Finalizado</option>
                <option value="postponed">Adiado</option>
              </select>
            </div>
            
            {/* Ordenação */}
            <div className="">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'teams' | 'status' | 'time')}
                className="mt-[3px] px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800"
              >
                <option value="status">Ordenar por Status</option>
                <option value="teams">Ordenar por Times</option>
                <option value="time">Ordenar por Tempo</option>
              </select>
            </div>
          </div>
        </div>



        {/* Erro */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">❌ {error}</p>
          </div>
        )}

        {/* Sucesso */}
        {updateSuccess && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800">✅ Partidas atualizadas com sucesso!</p>
          </div>
        )}

        {/* Lista de partidas */}
        {paginatedMatches.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {paginatedMatches.map((match, index) => (
                <MatchCard key={`${match.url}-${index}`} match={match} />
              ))}
            </div>

            {/* Paginação */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center space-x-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="flex items-center px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-gray-800"
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
                  className="flex items-center px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-gray-800"
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
              {searchTerm || statusFilter !== 'all' 
                ? 'Nenhuma partida encontrada com esses filtros.' 
                : 'Nenhuma partida disponível no momento.'}
            </p>
              <button
                onClick={handleRefresh}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Buscar Partidas
              </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
