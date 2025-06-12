'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import AnalysisCard from '@/components/AnalysisCard';
import { ScreenshotAnalysis } from '@/types/api';
import { mockScreenshotAnalyses } from '@/data/mockData';
import { RefreshCw, Search, Filter, Calendar, TrendingUp } from 'lucide-react';

export default function HistoricoPage() {
  const [analyses, setAnalyses] = useState<ScreenshotAnalysis[]>([]);
  const [filteredAnalyses, setFilteredAnalyses] = useState<ScreenshotAnalysis[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'team'>('date');
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Simular carregamento inicial
  useEffect(() => {
    setIsLoading(true);
    setTimeout(() => {
      setAnalyses(mockScreenshotAnalyses);
      setFilteredAnalyses(mockScreenshotAnalyses);
      setIsLoading(false);
      setLastUpdate(new Date());
    }, 1000);
  }, []);

  // Filtrar análises baseado na busca
  useEffect(() => {
    let filtered = analyses;

    if (searchTerm) {
      filtered = analyses.filter(analysis =>
        analysis.home_team.toLowerCase().includes(searchTerm.toLowerCase()) ||
        analysis.away_team.toLowerCase().includes(searchTerm.toLowerCase()) ||
        analysis.analysis_text.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Ordenar
    if (sortBy === 'date') {
      filtered = filtered.sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
    } else if (sortBy === 'team') {
      filtered = filtered.sort((a, b) => 
        a.home_team.localeCompare(b.home_team)
      );
    }

    setFilteredAnalyses(filtered);
  }, [analyses, searchTerm, sortBy]);

  const handleRefresh = async () => {
    setIsLoading(true);
    setTimeout(() => {
      setAnalyses(mockScreenshotAnalyses);
      setIsLoading(false);
      setLastUpdate(new Date());
    }, 1500);
  };

  // Função para obter times únicos (pode ser usada futuramente)
  // const getUniqueTeams = () => {
  //   const teams = new Set<string>();
  //   analyses.forEach(analysis => {
  //     teams.add(analysis.home_team);
  //     teams.add(analysis.away_team);
  //   });
  //   return Array.from(teams).sort();
  // };

  const getAnalysisStats = () => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    const todayAnalyses = analyses.filter(analysis => 
      new Date(analysis.created_at).toDateString() === today.toDateString()
    );
    
    const yesterdayAnalyses = analyses.filter(analysis => 
      new Date(analysis.created_at).toDateString() === yesterday.toDateString()
    );

    return {
      total: analyses.length,
      today: todayAnalyses.length,
      yesterday: yesterdayAnalyses.length,
      uniqueMatches: new Set(analyses.map(a => a.match_id)).size
    };
  };

  const stats = getAnalysisStats();

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header da página */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Histórico de Análises</h1>
            <p className="text-gray-600 mt-1">
              Visualize todas as análises técnicas geradas pelo assistente
            </p>
          </div>
          
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            {isLoading ? 'Atualizando...' : 'Atualizar'}
          </button>
        </div>

        {/* Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
                <div className="text-sm text-gray-600">Total de Análises</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center">
              <Calendar className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <div className="text-2xl font-bold text-gray-900">{stats.today}</div>
                <div className="text-sm text-gray-600">Hoje</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center">
              <Calendar className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <div className="text-2xl font-bold text-gray-900">{stats.yesterday}</div>
                <div className="text-sm text-gray-600">Ontem</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center">
              <Filter className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <div className="text-2xl font-bold text-gray-900">{stats.uniqueMatches}</div>
                <div className="text-sm text-gray-600">Partidas Únicas</div>
              </div>
            </div>
          </div>
        </div>

        {/* Filtros e busca */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 md:space-x-4">
            {/* Busca */}
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar por time ou conteúdo da análise..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            
            {/* Ordenação */}
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">
                Ordenar por:
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'date' | 'team')}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="date">Data (mais recente)</option>
                <option value="team">Time (A-Z)</option>
              </select>
            </div>
          </div>
          
          {/* Informações de filtro */}
          <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
            <div>
              Mostrando {filteredAnalyses.length} de {analyses.length} análises
              {searchTerm && (
                <span className="ml-2">
                  • Filtrado por: <span className="font-medium">&quot;{searchTerm}&quot;</span>
                </span>
              )}
            </div>
            <div>
              Última atualização: {lastUpdate.toLocaleTimeString('pt-BR')}
            </div>
          </div>
        </div>

        {/* Informações de desenvolvimento */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-blue-900">
                Modo de Desenvolvimento
              </h3>
              <p className="text-sm text-blue-700 mt-1">
                Exibindo análises mock. Conecte à API para dados reais.
              </p>
            </div>
          </div>
        </div>

        {/* Loading state */}
        {isLoading && analyses.length === 0 && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600">Carregando histórico de análises...</p>
            </div>
          </div>
        )}

        {/* Lista de análises */}
        {filteredAnalyses.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredAnalyses.map((analysis) => (
              <AnalysisCard
                key={analysis.id}
                analysis={analysis}
              />
            ))}
          </div>
        )}

        {/* Estado vazio */}
        {!isLoading && filteredAnalyses.length === 0 && analyses.length > 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Search className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhuma análise encontrada
            </h3>
            <p className="text-gray-600 mb-4">
              Tente ajustar os filtros de busca ou limpar o termo de pesquisa.
            </p>
            <button
              onClick={() => setSearchTerm('')}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Limpar filtros
            </button>
          </div>
        )}

        {/* Estado completamente vazio */}
        {!isLoading && analyses.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <TrendingUp className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhuma análise disponível
            </h3>
            <p className="text-gray-600 mb-4">
              Ainda não há análises técnicas geradas. Comece analisando algumas partidas!
            </p>
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Tentar novamente
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
} 