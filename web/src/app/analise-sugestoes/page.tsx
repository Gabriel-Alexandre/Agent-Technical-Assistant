'use client';

import { useSearchParams } from 'next/navigation';
import { useState, useEffect, useRef, Suspense } from 'react';
import Layout from '@/components/Layout';
import { 
  ArrowLeft, 
  Play, 
  Pause, 
  RefreshCw, 
  Clock, 
  TrendingUp, 
  Users, 
  Target, 
  Activity, 
  BarChart3,
  AlertCircle,
  CheckCircle,
  Zap,
  Timer,
  Trophy,
  MessageSquare,
  Calendar,
  ExternalLink
} from 'lucide-react';
import Link from 'next/link';
import ApiService from '@/services/api';

// Interfaces para os dados da nova API
interface MatchInfo {
  home_team: string;
  away_team: string;
  match_id: string;
  match_url: string;
  score: string;
  match_time: string;
  match_status: string;
}

interface MatchStatistic {
  home: string;
  away: string;
  name: string;
}

interface MatchEvent {
  time: string;
  player: string;
  type: string;
  team: 'home' | 'away';
}

interface DataAnalysisResponse {
  match_info: MatchInfo;
  match_statistics: Record<string, MatchStatistic>;
  match_events: MatchEvent[];
  analysis_text: string;
  analysis_type: string;
  generated_at: string;
  analysis_record_id?: string;
}

interface HistoryAnalysis {
  id: string;
  match_id: string;
  match_identifier: string;
  match_url: string;
  home_team: string;
  away_team: string;
  analysis_text: string;
  analysis_type: string;
  analysis_metadata: {
    match_info: MatchInfo;
    statistics: Record<string, MatchStatistic>;
    events: MatchEvent[];
  };
  created_at: string;
  updated_at: string;
}

function AnalyseSugestoesContent() {
  const searchParams = useSearchParams();
  
  // Parâmetros da URL
  const href = searchParams.get('href');
  const homeTeam = searchParams.get('home_team');
  const awayTeam = searchParams.get('away_team');
  const matchStatus = searchParams.get('match_status');
  const matchTime = searchParams.get('match_time');
  const homeScore = searchParams.get('home_score');
  const awayScore = searchParams.get('away_score');
  
  // Estados
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [autoAnalysis, setAutoAnalysis] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<DataAnalysisResponse | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<HistoryAnalysis[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [historyLimit, setHistoryLimit] = useState(10);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [matchId, setMatchId] = useState<string | null>(null);
  const [analysisCount, setAnalysisCount] = useState(0);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Extrair match_id do href
  const extractMatchIdFromHref = (href: string): string | null => {
    try {
      const decodedHref = decodeURIComponent(href);
      
      // Procurar por id: no final da URL
      const idMatch = decodedHref.match(/id:(\d+)/);
      if (idMatch && idMatch[1]) {
        return idMatch[1];
      }
      
      // Outros padrões
      const patterns = [
        /\/match\/(\d+)/,
        /match_id[=:](\d+)/,
        /\/(\d+)(?:\/|$)/,
      ];
      
      for (const pattern of patterns) {
        const match = decodedHref.match(pattern);
        if (match && match[1]) {
          return match[1];
        }
      }
      
      return null;
    } catch {
      return null;
    }
  };

  // Carregar histórico de análises existentes
  const loadExistingAnalyses = async (matchId: string) => {
    try {
      setIsLoadingHistory(true);
      setError(null);
      
      const response = await ApiService.getMatchDataAnalyses(matchId, historyLimit);
      
      if (response.success && response.data && response.data.length > 0) {
        setAnalysisHistory(response.data);
        setAnalysisCount(response.data.length);
        
        // Definir a análise mais recente como atual
        const latestAnalysis = response.data[0];
        if (latestAnalysis && latestAnalysis.analysis_metadata) {
          const convertedAnalysis: DataAnalysisResponse = {
            match_info: latestAnalysis.analysis_metadata.match_info,
            match_statistics: latestAnalysis.analysis_metadata.statistics,
            match_events: latestAnalysis.analysis_metadata.events,
            analysis_text: latestAnalysis.analysis_text,
            analysis_type: latestAnalysis.analysis_type,
            generated_at: latestAnalysis.created_at,
            analysis_record_id: latestAnalysis.id
          };
          
          setCurrentAnalysis(convertedAnalysis);
          setLastUpdate(new Date(latestAnalysis.created_at));
        }
      }
    } catch (err) {
      console.error('Erro ao carregar análises existentes:', err);
    } finally {
      setIsLoadingHistory(false);
      setIsInitialLoading(false);
    }
  };

  // Carregamento inicial
  useEffect(() => {
    if (href) {
      const extractedMatchId = extractMatchIdFromHref(href);
      if (extractedMatchId) {
        setMatchId(extractedMatchId);
        loadExistingAnalyses(extractedMatchId);
      } else {
        setIsInitialLoading(false);
      }
    } else {
      setIsInitialLoading(false);
    }
  }, [href, historyLimit]);

  // Realizar análise em tempo real
  const performRealTimeAnalysis = async () => {
    if (!href) return;
    
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const response = await ApiService.generateDataScrapingAnalysis(href);
      
      if (response.success && response.data) {
        setCurrentAnalysis(response.data);
        setLastUpdate(new Date());
        setAnalysisCount(prev => prev + 1);
        
        // Atualizar matchId se necessário
        if (response.data.match_info?.match_id) {
          setMatchId(response.data.match_info.match_id);
        }
        
        // Recarregar histórico após nova análise
        if (matchId || response.data.match_info?.match_id) {
          await loadExistingAnalyses(matchId || response.data.match_info.match_id);
        }
      } else {
        setError(response.message || 'Erro na análise');
      }
    } catch (err) {
      console.error('Erro na análise:', err);
      setError('Erro ao conectar com a API');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Iniciar/parar análise automática
  const toggleAutoAnalysis = () => {
    if (autoAnalysis) {
      // Parar análise automática
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      setAutoAnalysis(false);
    } else {
      // Iniciar análise automática
      setAutoAnalysis(true);
      // Fazer análise imediatamente
      performRealTimeAnalysis();
      
      // Configurar intervalo de 1 minuto
      intervalRef.current = setInterval(() => {
        performRealTimeAnalysis();
      }, 60000); // 60 segundos
    }
  };

  // Cleanup no unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Formatar texto de análise
  const formatAnalysisText = (text: string) => {
    return text.split('\n').map((line, index) => {
      if (line.startsWith('🏆')) {
        return <h2 key={index} className="text-2xl font-bold text-gray-900 mb-4 flex items-center"><Trophy className="h-6 w-6 mr-2 text-yellow-600" />{line}</h2>;
      } else if (line.startsWith('📊')) {
        return <h3 key={index} className="text-lg font-semibold text-blue-800 mb-2 mt-4 flex items-center"><BarChart3 className="h-5 w-5 mr-2" />{line}</h3>;
      } else if (line.startsWith('🎯')) {
        return <h3 key={index} className="text-lg font-semibold text-green-800 mb-2 mt-4 flex items-center"><Target className="h-5 w-5 mr-2" />{line}</h3>;
      } else if (line.startsWith('• ')) {
        return <li key={index} className="text-gray-700 mb-1 ml-4">{line.replace('• ', '')}</li>;
      } else if (line.trim() === '') {
        return <br key={index} />;
      } else {
        return <p key={index} className="text-gray-700 mb-2">{line}</p>;
      }
    });
  };

  // Formatar data/hora
  const formatDateTime = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return 'Data inválida';
    }
  };

  // Carregar mais histórico
  const loadMoreHistory = () => {
    setHistoryLimit(prev => prev + 10);
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header aprimorado */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                href="/"
                className="flex items-center px-3 py-2 bg-white/20 rounded-md hover:bg-white/30 transition-colors"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Voltar
              </Link>
              <div>
                <h1 className="text-3xl font-bold">Análise Técnica em Tempo Real</h1>
                <p className="text-blue-100 mt-1">
                  {homeTeam && awayTeam ? `${homeTeam} vs ${awayTeam}` : 'Monitoramento avançado da partida'}
                </p>
                {matchStatus && (
                  <div className="flex items-center mt-2 space-x-4">
                    <span className="bg-white/20 px-3 py-1 rounded-full text-sm">
                      Status: {matchStatus === 'in_progress' ? 'Ao Vivo' : matchStatus === 'not_started' ? 'Não Iniciado' : 'Finalizado'}
                    </span>
                    {matchTime && (
                      <span className="bg-white/20 px-3 py-1 rounded-full text-sm flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {matchTime}
                      </span>
                    )}
                    {homeScore && awayScore && (
                      <span className="bg-white/20 px-3 py-1 rounded-full text-sm font-bold">
                        {homeScore} - {awayScore}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Controle principal */}
            <div className="text-center">
              <button
                onClick={toggleAutoAnalysis}
                disabled={isAnalyzing}
                className={`flex items-center px-6 py-3 rounded-lg font-semibold transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed ${
                  autoAnalysis 
                    ? 'bg-red-500 hover:bg-red-600 text-white' 
                    : 'bg-green-500 hover:bg-green-600 text-white'
                }`}
              >
                {autoAnalysis ? (
                  <>
                    <Pause className="h-5 w-5 mr-2" />
                    Parar Análise Automática
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5 mr-2" />
                    Iniciar Análise em Tempo Real
                  </>
                )}
              </button>
              
              {autoAnalysis && (
                <div className="mt-2 text-sm text-blue-100">
                  <div className="flex items-center justify-center">
                    <Activity className="h-4 w-4 mr-1 animate-pulse" />
                    Próxima análise em {Math.floor((60 - new Date().getSeconds()) / 1) || 60}s
                  </div>
                  <div className="text-xs">
                    {analysisCount} análise(s) realizadas
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Loading inicial */}
        {isInitialLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Carregando análises da partida</h3>
              <p className="text-gray-600">Verificando histórico de análises existentes...</p>
            </div>
          </div>
        )}

        {/* Status da análise em andamento */}
        {isAnalyzing && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center">
              <RefreshCw className="h-5 w-5 text-yellow-600 mr-3 animate-spin" />
              <div>
                <span className="text-yellow-800 font-medium">🔄 Coletando dados em tempo real...</span>
                <p className="text-yellow-700 text-sm">Extraindo estatísticas e eventos da partida</p>
              </div>
            </div>
          </div>
        )}

        {/* Status da análise automática */}
        {autoAnalysis && !isAnalyzing && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Zap className="h-5 w-5 text-green-600 mr-3 animate-pulse" />
                <div>
                  <span className="text-green-800 font-medium">🤖 Monitoramento automático ativo</span>
                  <p className="text-green-700 text-sm">Gerando análises técnicas a cada minuto</p>
                </div>
              </div>
              {lastUpdate && (
                <div className="text-sm text-green-600 flex items-center">
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Última atualização: {lastUpdate.toLocaleTimeString('pt-BR')}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Erro */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-600 mr-3" />
              <div className="text-red-800">
                <strong>Erro na análise:</strong> {error}
              </div>
            </div>
          </div>
        )}

        {/* Análise atual detalhada */}
        {currentAnalysis && !isInitialLoading && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Coluna principal - Análise */}
            <div className="lg:col-span-2 space-y-6">
              {/* Informações da partida */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-900 flex items-center">
                    <Users className="h-6 w-6 mr-2 text-blue-600" />
                    Informações da Partida
                  </h3>
                  <div className="text-sm text-gray-500 flex items-center">
                    <Calendar className="h-4 w-4 mr-1" />
                    {formatDateTime(currentAnalysis.generated_at)}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-lg font-bold text-blue-900">
                      {currentAnalysis.match_info.home_team}
                    </div>
                    <div className="text-sm text-blue-700">Casa</div>
                  </div>
                  
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">
                      {currentAnalysis.match_info.score}
                    </div>
                    <div className="text-sm text-gray-600">
                      {currentAnalysis.match_info.match_status}
                    </div>
                  </div>
                  
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <div className="text-lg font-bold text-red-900">
                      {currentAnalysis.match_info.away_team}
                    </div>
                    <div className="text-sm text-red-700">Fora</div>
                  </div>
                </div>

                <div className="mt-4 text-center">
                  <a 
                    href={currentAnalysis.match_info.match_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors text-sm"
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Ver no SofaScore
                  </a>
                </div>
              </div>

              {/* Análise técnica */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                  <MessageSquare className="h-6 w-6 mr-2 text-green-600" />
                  Análise Técnica Avançada
                </h3>
                <div className="prose max-w-none">
                  {formatAnalysisText(currentAnalysis.analysis_text)}
                </div>
              </div>
            </div>

            {/* Coluna lateral - Estatísticas e Eventos */}
            <div className="space-y-6">
              {/* Estatísticas principais */}
              {Object.keys(currentAnalysis.match_statistics).length > 0 && (
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                    <BarChart3 className="h-5 w-5 mr-2 text-purple-600" />
                    Estatísticas em Tempo Real
                  </h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {Object.entries(currentAnalysis.match_statistics).slice(0, 10).map(([key, stat]) => (
                      <div key={key} className="bg-gray-50 rounded-lg p-3">
                        <div className="text-sm font-medium text-gray-700 mb-2">{stat.name}</div>
                        <div className="flex justify-between items-center">
                          <div className="text-blue-600 font-semibold">{stat.home}</div>
                          <div className="text-red-600 font-semibold">{stat.away}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Eventos recentes */}
              {currentAnalysis.match_events.length > 0 && (
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                    <Activity className="h-5 w-5 mr-2 text-orange-600" />
                    Eventos Recentes
                  </h3>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {currentAnalysis.match_events.slice(0, 10).map((event, index) => (
                      <div key={index} className="flex items-center space-x-3 p-2 bg-gray-50 rounded-lg">
                        <div className={`w-2 h-2 rounded-full ${event.team === 'home' ? 'bg-blue-500' : 'bg-red-500'}`}></div>
                        <div className="flex-1">
                          <div className="text-sm font-medium text-gray-900">{event.type}</div>
                          <div className="text-xs text-gray-600">{event.player}</div>
                        </div>
                        <div className="text-xs font-medium text-gray-500">{event.time}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Histórico de análises aprimorado */}
        {analysisHistory.length > 0 && !isInitialLoading && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900 flex items-center">
                <TrendingUp className="h-6 w-6 mr-2 text-indigo-600" />
                Histórico de Análises
              </h3>
              <div className="flex items-center text-sm text-gray-500">
                <Timer className="h-4 w-4 mr-1" />
                {analysisHistory.length} análise(s) registradas
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysisHistory.map((item, index) => (
                <div key={item.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium text-gray-900 text-sm">
                      {item.home_team} vs {item.away_team}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatDateTime(item.created_at)}
                    </div>
                  </div>
                  
                  {item.analysis_metadata?.match_info && (
                    <div className="text-xs text-gray-600 mb-2">
                      {item.analysis_metadata.match_info.score} • {item.analysis_metadata.match_info.match_status}
                    </div>
                  )}
                  
                  <div className="text-sm text-gray-600 line-clamp-2">
                    {item.analysis_text.substring(0, 150)}...
                  </div>
                  
                  <div className="mt-2 flex items-center justify-between">
                    <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                      {item.analysis_type}
                    </span>
                    {item.analysis_metadata?.statistics && (
                      <span className="text-xs text-gray-500">
                        {Object.keys(item.analysis_metadata.statistics).length} estatísticas
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Botão para carregar mais */}
            <div className="mt-6 text-center">
              <button
                onClick={loadMoreHistory}
                disabled={isLoadingHistory}
                className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                {isLoadingHistory ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin inline" />
                    Carregando...
                  </>
                ) : (
                  'Carregar Mais Análises'
                )}
              </button>
            </div>
          </div>
        )}

        {/* Estado vazio melhorado */}
        {!currentAnalysis && !isAnalyzing && !error && !isInitialLoading && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Activity className="h-20 w-20 mx-auto" />
            </div>
            <h3 className="text-xl font-medium text-gray-900 mb-2">
              Pronto para análise técnica
            </h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Esta partida ainda não possui análises. Clique em "Iniciar Análise em Tempo Real" para começar o monitoramento automático.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 max-w-lg mx-auto">
              <div className="flex items-start space-x-3">
                <Zap className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
                <div className="text-left">
                  <h4 className="font-semibold text-blue-900 mb-2">Análise em Tempo Real</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Coleta automática de dados a cada minuto</li>
                    <li>• Estatísticas detalhadas da partida</li>
                    <li>• Eventos e substituições em tempo real</li>
                    <li>• Recomendações táticas baseadas em IA</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default function AnalyseSugestoesPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AnalyseSugestoesContent />
    </Suspense>
  );
} 