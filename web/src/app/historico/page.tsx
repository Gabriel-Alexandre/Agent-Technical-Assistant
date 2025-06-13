'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { ScreenshotAnalysis } from '@/types/api';
import { RefreshCw, Search, Filter, Calendar, TrendingUp, AlertCircle, Clock, Users, ChevronDown, ChevronUp, ExternalLink, FileText } from 'lucide-react';
import ApiService from '@/services/api';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface GroupedMatch {
  match_id: string;
  home_team: string;
  away_team: string;
  match_url: string;
  analyses: ScreenshotAnalysis[];
  latest_analysis: string;
  total_analyses: number;
}

export default function HistoricoPage() {
  const [analyses, setAnalyses] = useState<ScreenshotAnalysis[]>([]);
  const [groupedMatches, setGroupedMatches] = useState<GroupedMatch[]>([]);
  const [filteredMatches, setFilteredMatches] = useState<GroupedMatch[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'team' | 'analyses'>('date');
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(100);
  const [expandedMatches, setExpandedMatches] = useState<Set<string>>(new Set());

  // Carregar análises da API
  const loadAnalyses = async () => {
    try {
      setError(null);
      const response = await ApiService.getAllScreenshotAnalyses(limit);
      
      if (response.success && response.data) {
        setAnalyses(response.data);
        setLastUpdate(new Date());
      } else {
        setError(response.message || 'Erro ao carregar análises');
      }
    } catch (err) {
      console.error('Erro ao carregar análises:', err);
      setError('Erro ao conectar com a API');
    }
  };

  // Agrupar análises por partida
  const groupAnalysesByMatch = (analyses: ScreenshotAnalysis[]): GroupedMatch[] => {
    const grouped = analyses.reduce((acc, analysis) => {
      const matchId = analysis.match_id;
      
      if (!acc[matchId]) {
        acc[matchId] = {
          match_id: matchId,
          home_team: analysis.home_team,
          away_team: analysis.away_team,
          match_url: analysis.match_url,
          analyses: [],
          latest_analysis: analysis.created_at,
          total_analyses: 0
        };
      }
      
      acc[matchId].analyses.push(analysis);
      acc[matchId].total_analyses = acc[matchId].analyses.length;
      
      // Manter a análise mais recente
      if (new Date(analysis.created_at) > new Date(acc[matchId].latest_analysis)) {
        acc[matchId].latest_analysis = analysis.created_at;
      }
      
      return acc;
    }, {} as Record<string, GroupedMatch>);

    return Object.values(grouped);
  };

  // Carregamento inicial
  useEffect(() => {
    const initialLoad = async () => {
      setIsInitialLoading(true);
      await loadAnalyses();
      setIsInitialLoading(false);
    };
    
    initialLoad();
  }, [limit]);

  // Agrupar e filtrar análises
  useEffect(() => {
    const grouped = groupAnalysesByMatch(analyses);
    setGroupedMatches(grouped);

    let filtered = grouped;

    if (searchTerm) {
      filtered = grouped.filter(match =>
        match.home_team.toLowerCase().includes(searchTerm.toLowerCase()) ||
        match.away_team.toLowerCase().includes(searchTerm.toLowerCase()) ||
        match.analyses.some(analysis => 
          analysis.analysis_text.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Ordenar
    if (sortBy === 'date') {
      filtered = filtered.sort((a, b) => 
        new Date(b.latest_analysis).getTime() - new Date(a.latest_analysis).getTime()
      );
    } else if (sortBy === 'team') {
      filtered = filtered.sort((a, b) => 
        a.home_team.localeCompare(b.home_team)
      );
    } else if (sortBy === 'analyses') {
      filtered = filtered.sort((a, b) => 
        b.total_analyses - a.total_analyses
      );
    }

    setFilteredMatches(filtered);
  }, [analyses, searchTerm, sortBy]);

  const handleRefresh = async () => {
    setIsLoading(true);
    await loadAnalyses();
    setIsLoading(false);
  };

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
      uniqueMatches: groupedMatches.length
    };
  };

  const loadMoreAnalyses = () => {
    setLimit(prev => prev + 100);
  };

  const toggleMatchExpansion = (matchId: string) => {
    const newExpanded = new Set(expandedMatches);
    if (newExpanded.has(matchId)) {
      newExpanded.delete(matchId);
    } else {
      newExpanded.add(matchId);
    }
    setExpandedMatches(newExpanded);
  };

  const formatAnalysisTime = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { 
        addSuffix: true, 
        locale: ptBR 
      });
    } catch {
      return 'Tempo indisponível';
    }
  };

  const formatAnalysisText = (text: string) => {
    // Remover o JSON do final se existir
    const cleanText = text.replace(/```json[\s\S]*?```/g, '').trim();
    
    // Converter markdown básico para HTML
    return cleanText
      .replace(/## (.*?)(\n|$)/g, '<h3 class="text-lg font-semibold text-gray-800 mb-2 mt-4">$1</h3>')
      .replace(/### (.*?)(\n|$)/g, '<h4 class="text-base font-medium text-gray-700 mb-2 mt-3">$1</h4>')
      .replace(/• (.*?)(\n|$)/g, '<li class="text-gray-700 mb-1 ml-4">$1</li>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n\n/g, '<br /><br />')
      .replace(/\n/g, '<br />');
  };

  const getPreviewText = (text: string, maxLength: number = 150) => {
    const cleanText = text.replace(/```json[\s\S]*?```/g, '').trim();
    if (cleanText.length <= maxLength) return cleanText;
    return cleanText.substring(0, maxLength) + '...';
  };

  const stats = getAnalysisStats();

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header da página */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Histórico por Partidas</h1>
            <p className="text-gray-600 mt-1">
              Análises agrupadas por partidas únicas
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

        {/* Erro */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-600 mr-3" />
              <div className="text-red-800">
                <strong>Erro:</strong> {error}
              </div>
            </div>
          </div>
        )}

        {/* Loading inicial */}
        {isInitialLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600">Carregando histórico de análises...</p>
            </div>
          </div>
        )}

        {/* Conteúdo principal - só mostra se não está carregando inicialmente */}
        {!isInitialLoading && (
          <>
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
                  <Users className="h-8 w-8 text-purple-600" />
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
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800"
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
                    onChange={(e) => setSortBy(e.target.value as 'date' | 'team' | 'analyses')}
                    className="px-2 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800"
                  >
                    <option value="date">Última análise</option>
                    <option value="team">Time (A-Z)</option>
                    <option value="analyses">Mais análises</option>
                  </select>
                </div>
              </div>
              
              {/* Informações de filtro */}
              <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
                <div>
                  Mostrando {filteredMatches.length} partida(s) de {groupedMatches.length} total
                  {searchTerm && (
                    <span className="ml-2">
                      • Filtrado por: <span className="font-medium">&quot;{searchTerm}&quot;</span>
                    </span>
                  )}
                </div>
                {lastUpdate && (
                  <div>
                    Última atualização: {lastUpdate.toLocaleTimeString('pt-BR')}
                  </div>
                )}
              </div>
            </div>

            {/* Lista de partidas agrupadas */}
            {filteredMatches.length > 0 && (
              <div className="space-y-4">
                {filteredMatches.map((match) => {
                  const isExpanded = expandedMatches.has(match.match_id);
                  const latestAnalysis = match.analyses.sort((a, b) => 
                    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                  )[0];

                  return (
                    <div key={match.match_id} className="bg-white rounded-lg shadow-sm border">
                      {/* Header da partida */}
                      <div className="p-6">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center justify-center space-x-4 mb-4">
                              <div className="text-center">
                                <h3 className="font-bold text-xl text-gray-900">{match.home_team}</h3>
                              </div>
                              <div className="text-3xl font-bold text-gray-400">VS</div>
                              <div className="text-center">
                                <h3 className="font-bold text-xl text-gray-900">{match.away_team}</h3>
                              </div>
                            </div>
                            
                            {/* Informações da partida */}
                            <div className="flex items-center justify-between text-sm text-gray-500">
                              <div className="flex items-center space-x-4">
                                <div className="flex items-center">
                                  <Clock className="h-4 w-4 mr-1" />
                                  <span>Última análise: {formatAnalysisTime(match.latest_analysis)}</span>
                                </div>
                                <div className="flex items-center">
                                  <FileText className="h-4 w-4 mr-1" />
                                  <span>{match.total_analyses} análise(s)</span>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <a
                                  href={match.match_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                                >
                                  <ExternalLink className="h-3 w-3 mr-1" />
                                  Ver Partida
                                </a>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Prévia da análise mais recente */}
                        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-700">Análise mais recente:</span>
                            <span className="text-xs text-gray-500">
                              {formatAnalysisTime(latestAnalysis.created_at)}
                            </span>
                          </div>
                          <div 
                            className="text-sm text-gray-600 leading-relaxed"
                            dangerouslySetInnerHTML={{ 
                              __html: formatAnalysisText(getPreviewText(latestAnalysis.analysis_text))
                            }}
                          />
                        </div>

                        {/* Botão expandir/recolher */}
                        <div className="mt-4 text-center">
                          <button
                            onClick={() => toggleMatchExpansion(match.match_id)}
                            className="flex items-center mx-auto px-4 py-2 text-sm text-blue-600 hover:text-blue-800 transition-colors"
                          >
                            {isExpanded ? (
                              <>
                                <ChevronUp className="h-4 w-4 mr-1" />
                                Ocultar todas as análises
                              </>
                            ) : (
                              <>
                                <ChevronDown className="h-4 w-4 mr-1" />
                                Ver todas as {match.total_analyses} análise(s)
                              </>
                            )}
                          </button>
                        </div>
                      </div>

                      {/* Lista expandida de análises */}
                      {isExpanded && (
                        <div className="border-t bg-gray-50">
                          <div className="p-6">
                            <h4 className="font-medium text-gray-900 mb-4">
                              Todas as análises ({match.total_analyses})
                            </h4>
                            <div className="space-y-4">
                              {match.analyses
                                .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                                .map((analysis, index) => (
                                <div key={analysis.id} className="bg-white rounded-lg p-4 border">
                                  <div className="flex items-center justify-between mb-3">
                                    <span className="text-sm font-medium text-gray-700">
                                      Análise #{match.total_analyses - index}
                                    </span>
                                    <span className="text-xs text-gray-500">
                                      {formatAnalysisTime(analysis.created_at)}
                                    </span>
                                  </div>
                                  <div 
                                    className="text-sm text-gray-600 leading-relaxed"
                                    dangerouslySetInnerHTML={{ 
                                      __html: formatAnalysisText(analysis.analysis_text)
                                    }}
                                  />
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Botão carregar mais */}
            {analyses.length > 0 && analyses.length >= limit && (
              <div className="text-center">
                <button
                  onClick={loadMoreAnalyses}
                  disabled={isLoading}
                  className="px-6 py-3 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 transition-colors"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin inline" />
                      Carregando...
                    </>
                  ) : (
                    'Carregar Mais Análises'
                  )}
                </button>
              </div>
            )}

            {/* Estado vazio - busca sem resultados */}
            {!isLoading && filteredMatches.length === 0 && groupedMatches.length > 0 && (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <Search className="h-16 w-16 mx-auto" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Nenhuma partida encontrada
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
            {!isLoading && groupedMatches.length === 0 && !error && (
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
          </>
        )}
      </div>
    </Layout>
  );
} 