'use client';

import { useState, useEffect, useMemo } from 'react';
import Layout from '@/components/Layout';
import { ScreenshotAnalysis } from '@/types/api';
import { RefreshCw, Search, Clock, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
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
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'team'>('date');
  const [error, setError] = useState<string | null>(null);
  const [expandedMatches, setExpandedMatches] = useState<Set<string>>(new Set());

  // Carregar análises da API
  const loadAnalyses = async () => {
    try {
      setError(null);
      const response = await ApiService.getAllScreenshotAnalyses(100);
      
      if (response.success && response.data) {
        setAnalyses(response.data);
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
  }, []);

  // Filtrar e ordenar partidas
  const filteredMatches = useMemo(() => {
    const grouped = groupAnalysesByMatch(analyses);
    
    let filtered = grouped;

    if (searchTerm) {
      filtered = grouped.filter(match =>
        match.home_team.toLowerCase().includes(searchTerm.toLowerCase()) ||
        match.away_team.toLowerCase().includes(searchTerm.toLowerCase())
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
    }

    return filtered;
  }, [analyses, searchTerm, sortBy]);

  const handleRefresh = async () => {
    setIsLoading(true);
    await loadAnalyses();
    setIsLoading(false);
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
      .replace(/## (.*?)(\n|$)/g, '<h3 class="text-base font-semibold text-gray-800 mb-2">$1</h3>')
      .replace(/### (.*?)(\n|$)/g, '<h4 class="text-sm font-medium text-gray-700 mb-1">$1</h4>')
      .replace(/• (.*?)(\n|$)/g, '<li class="text-gray-700 mb-1 ml-4">$1</li>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n\n/g, '<br /><br />')
      .replace(/\n/g, '<br />');
  };

  const getPreviewText = (text: string, maxLength: number = 200) => {
    const cleanText = text.replace(/```json[\s\S]*?```/g, '').trim();
    if (cleanText.length <= maxLength) return cleanText;
    return cleanText.substring(0, maxLength) + '...';
  };

  if (isInitialLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Carregando histórico...</p>
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
            <h1 className="text-2xl font-bold text-gray-900">Histórico de Análises</h1>
            <p className="text-gray-600">
              {filteredMatches.length} partidas analisadas
            </p>
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
            
            {/* Ordenação */}
            <div>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'date' | 'team')}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800"
              >
                <option value="date">Mais recentes</option>
                <option value="team">Por time</option>
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
        {filteredMatches.length > 0 ? (
          <div className="space-y-4">
            {filteredMatches.map((match) => {
              const isExpanded = expandedMatches.has(match.match_id);
              const latestAnalysis = match.analyses.sort((a, b) => 
                new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
              )[0];

              return (
                <div key={`${match.match_id}-${match.home_team}-${match.away_team}`} className="bg-white rounded-lg shadow-sm border">
                  <div className="p-4">
                    {/* Times */}
                    <div className="flex items-center justify-center space-x-3 mb-3">
                      <div className="text-center flex-1">
                        <h3 className="font-semibold text-gray-900">{match.home_team}</h3>
                        <span className="text-xs text-gray-500">Casa</span>
                      </div>
                      <div className="text-lg font-bold text-gray-400">×</div>
                      <div className="text-center flex-1">
                        <h3 className="font-semibold text-gray-900">{match.away_team}</h3>
                        <span className="text-xs text-gray-500">Fora</span>
                      </div>
                    </div>
                    
                    {/* Info */}
                    <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        <span>{formatAnalysisTime(match.latest_analysis)}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span>{match.total_analyses} análise(s)</span>
                        <a
                          href={match.match_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center px-2 py-1 text-xs bg-gray-100 rounded hover:bg-gray-200"
                        >
                          <ExternalLink className="h-3 w-3 mr-1" />
                          SofaScore
                        </a>
                      </div>
                    </div>

                    {/* Prévia da análise */}
                    <div className="p-3 bg-gray-50 rounded text-sm">
                      <div 
                        className="text-gray-600"
                        dangerouslySetInnerHTML={{ 
                          __html: formatAnalysisText(getPreviewText(latestAnalysis.analysis_text))
                        }}
                      />
                    </div>

                    {/* Botão expandir */}
                    {match.total_analyses > 1 && (
                      <div className="mt-3 text-center">
                        <button
                          onClick={() => toggleMatchExpansion(match.match_id)}
                          className="flex items-center mx-auto px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
                        >
                          {isExpanded ? (
                            <>
                              <ChevronUp className="h-4 w-4 mr-1" />
                              Ocultar análises
                            </>
                          ) : (
                            <>
                              <ChevronDown className="h-4 w-4 mr-1" />
                              Ver todas ({match.total_analyses})
                            </>
                          )}
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Análises expandidas */}
                  {isExpanded && (
                    <div className="border-t bg-gray-50 p-4">
                      <div className="space-y-3">
                        {match.analyses
                          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                          .map((analysis, index) => (
                          <div key={`${analysis.id}-${index}`} className="bg-white rounded p-3 border">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium text-gray-700">
                                Análise #{match.total_analyses - index}
                              </span>
                              <span className="text-xs text-gray-500">
                                {formatAnalysisTime(analysis.created_at)}
                              </span>
                            </div>
                            <div 
                              className="text-sm text-gray-600"
                              dangerouslySetInnerHTML={{ 
                                __html: formatAnalysisText(analysis.analysis_text)
                              }}
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">
              {searchTerm ? 'Nenhuma partida encontrada com esse filtro.' : 'Nenhuma análise disponível.'}
            </p>
            {searchTerm ? (
              <button
                onClick={() => setSearchTerm('')}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Limpar filtro
              </button>
            ) : (
              <button
                onClick={handleRefresh}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Tentar novamente
              </button>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
} 