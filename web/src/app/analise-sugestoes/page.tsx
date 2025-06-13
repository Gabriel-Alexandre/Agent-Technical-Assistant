'use client';

import { useSearchParams } from 'next/navigation';
import { useState, useEffect, useRef } from 'react';
import Layout from '@/components/Layout';
import { ArrowLeft, Play, Pause, RefreshCw, Clock, TrendingUp, Users, Target, Activity } from 'lucide-react';
import Link from 'next/link';
import ApiService from '@/services/api';

interface MatchInfo {
  home_team: string;
  away_team: string;
  match_id: string;
  match_url: string;
}

interface VisualAnalysisData {
  home_team: string;
  away_team: string;
  score_home?: string;
  score_away?: string;
  match_time?: string;
  match_status?: string;
  possession_home?: string;
  possession_away?: string;
  visible_stats?: string[];
}

interface AnalysisData {
  match_info: MatchInfo;
  screenshot_info: {
    size_bytes: number;
    file_size_kb: number;
    analysis_method: string;
  };
  visual_analysis_data: VisualAnalysisData;
  analysis_text: string;
  analysis_type: string;
  generated_at: string;
  analysis_record_id?: string;
}

interface HistoryItem {
  id: string;
  match_id: string;
  home_team: string;
  away_team: string;
  analysis_text: string;
  created_at: string;
  analysis_type?: string;
}

export default function AnalyseSugestoesPage() {
  const searchParams = useSearchParams();
  const href = searchParams.get('href');
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [autoAnalysis, setAutoAnalysis] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisData | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<HistoryItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [historyLimit, setHistoryLimit] = useState(10);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Função para fazer análise
  const performAnalysis = async () => {
    if (!href) return;
    
    setIsAnalyzing(true);
    setError(null);
    
    try {
      console.log('Fazendo análise para href:', href);
      
      // Fazer requisição para a API de análise
      const response = await ApiService.generateScreenshotAnalysis(href);
      
      if (response.success && response.data) {
        setCurrentAnalysis(response.data);
        setLastUpdate(new Date());
        
        // Recarregar histórico após nova análise
        await loadAnalysisHistory();
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

  // Função para carregar histórico
  const loadAnalysisHistory = async () => {
    if (!currentAnalysis?.match_info?.match_id) return;
    
    setIsLoadingHistory(true);
    
    try {
      const response = await ApiService.getMatchScreenshotAnalyses(
        currentAnalysis.match_info.match_id, 
        historyLimit
      );
      
      if (response.success && response.data) {
        setAnalysisHistory(response.data);
      }
    } catch (err) {
      console.error('Erro ao carregar histórico:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // Controlar análise automática
  useEffect(() => {
    if (autoAnalysis && href) {
      // Fazer análise imediatamente
      performAnalysis();
      
      // Configurar intervalo de 1 minuto
      intervalRef.current = setInterval(() => {
        performAnalysis();
      }, 60000); // 60 segundos
      
      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }
  }, [autoAnalysis, href]);

  // Carregar histórico quando análise atual mudar
  useEffect(() => {
    if (currentAnalysis?.match_info?.match_id) {
      loadAnalysisHistory();
    }
  }, [currentAnalysis?.match_info?.match_id, historyLimit]);

  // Cleanup no unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const toggleAutoAnalysis = () => {
    setAutoAnalysis(!autoAnalysis);
  };

  const formatAnalysisText = (text: string) => {
    // Remover o JSON do final se existir
    const cleanText = text.replace(/```json[\s\S]*?```/g, '').trim();
    
    // Converter markdown básico para JSX
    return cleanText.split('\n').map((line, index) => {
      if (line.startsWith('## ')) {
        return <h2 key={index} className="text-2xl font-bold text-gray-900 mb-4">{line.replace('## ', '')}</h2>;
      } else if (line.startsWith('### ')) {
        return <h3 key={index} className="text-lg font-semibold text-gray-800 mb-2 mt-4">{line.replace('### ', '')}</h3>;
      } else if (line.startsWith('• ')) {
        return <li key={index} className="text-gray-700 mb-1">{line.replace('• ', '')}</li>;
      } else if (line.trim() === '') {
        return <br key={index} />;
      } else {
        return <p key={index} className="text-gray-700 mb-2">{line}</p>;
      }
    });
  };

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

  const loadMoreHistory = () => {
    setHistoryLimit(prev => prev + 10);
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header da página */}
        <div className="flex items-center justify-between">
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
                Análise técnica em tempo real da partida
              </p>
            </div>
          </div>

          {/* Controles */}
          <div className="flex items-center space-x-3">
            <button
              onClick={performAnalysis}
              disabled={isAnalyzing}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isAnalyzing ? 'animate-spin' : ''}`} />
              {isAnalyzing ? 'Analisando...' : 'Analisar Agora'}
            </button>

            <button
              onClick={toggleAutoAnalysis}
              className={`flex items-center px-4 py-2 rounded-md transition-colors ${
                autoAnalysis 
                  ? 'bg-red-600 text-white hover:bg-red-700' 
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              {autoAnalysis ? (
                <>
                  <Pause className="h-4 w-4 mr-2" />
                  Parar Auto-Análise
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Iniciar Auto-Análise
                </>
              )}
            </button>
          </div>
        </div>

        {/* Status da análise automática */}
        {autoAnalysis && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center">
              <Activity className="h-5 w-5 text-green-600 mr-3 animate-pulse" />
              <div>
                <span className="text-green-800 font-medium">Análise automática ativa</span>
                <p className="text-green-700 text-sm">Nova análise a cada minuto</p>
              </div>
              {lastUpdate && (
                <div className="ml-auto text-sm text-green-600">
                  Última atualização: {lastUpdate.toLocaleTimeString('pt-BR')}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Informações da partida */}
        {href && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Partida Selecionada</h3>
            <div className="bg-gray-50 rounded-md p-4">
              <p className="text-sm text-gray-600 mb-2">Link original:</p>
              <code className="text-sm bg-gray-100 px-2 py-1 rounded break-all">{decodeURIComponent(href)}</code>
            </div>
          </div>
        )}

        {/* Erro */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <div className="text-red-800">
                <strong>Erro:</strong> {error}
              </div>
            </div>
          </div>
        )}

        {/* Análise atual */}
        {currentAnalysis && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">Análise Atual</h3>
              <div className="text-sm text-gray-500">
                <Clock className="h-4 w-4 inline mr-1" />
                {formatDateTime(currentAnalysis.generated_at)}
              </div>
            </div>

            {/* Informações da partida */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Users className="h-5 w-5 text-blue-600 mr-2" />
                  <span className="font-medium text-blue-900">Times</span>
                </div>
                <p className="text-blue-800">
                  {currentAnalysis.match_info.home_team} vs {currentAnalysis.match_info.away_team}
                </p>
              </div>

              {currentAnalysis.visual_analysis_data.score_home && currentAnalysis.visual_analysis_data.score_away && (
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <Target className="h-5 w-5 text-green-600 mr-2" />
                    <span className="font-medium text-green-900">Placar</span>
                  </div>
                  <p className="text-green-800 text-xl font-bold">
                    {currentAnalysis.visual_analysis_data.score_home} - {currentAnalysis.visual_analysis_data.score_away}
                  </p>
                </div>
              )}

              {currentAnalysis.visual_analysis_data.match_time && (
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <Clock className="h-5 w-5 text-purple-600 mr-2" />
                    <span className="font-medium text-purple-900">Tempo</span>
                  </div>
                  <p className="text-purple-800">
                    {currentAnalysis.visual_analysis_data.match_time}
                  </p>
                </div>
              )}
            </div>

            {/* Posse de bola */}
            {currentAnalysis.visual_analysis_data.possession_home && currentAnalysis.visual_analysis_data.possession_away && (
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-3">Posse de Bola</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {currentAnalysis.visual_analysis_data.possession_home}
                    </div>
                    <div className="text-sm text-gray-600">
                      {currentAnalysis.match_info.home_team}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {currentAnalysis.visual_analysis_data.possession_away}
                    </div>
                    <div className="text-sm text-gray-600">
                      {currentAnalysis.match_info.away_team}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Análise técnica */}
            <div className="border-t pt-6">
              <h4 className="font-medium text-gray-900 mb-4">Sugestões Técnicas</h4>
              <div className="prose max-w-none">
                {formatAnalysisText(currentAnalysis.analysis_text)}
              </div>
            </div>

            {/* Estatísticas visíveis */}
            {currentAnalysis.visual_analysis_data.visible_stats && currentAnalysis.visual_analysis_data.visible_stats.length > 0 && (
              <div className="border-t pt-6 mt-6">
                <h4 className="font-medium text-gray-900 mb-3">Estatísticas Analisadas</h4>
                <div className="flex flex-wrap gap-2">
                  {currentAnalysis.visual_analysis_data.visible_stats.map((stat, index) => (
                    <span 
                      key={index}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                    >
                      {stat}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Histórico de análises */}
        {analysisHistory.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">Histórico de Análises</h3>
              <div className="flex items-center text-sm text-gray-500">
                <TrendingUp className="h-4 w-4 mr-1" />
                {analysisHistory.length} análise(s)
              </div>
            </div>

            <div className="space-y-4">
              {analysisHistory.map((item, index) => (
                <div key={item.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium text-gray-900">
                      {item.home_team} vs {item.away_team}
                    </div>
                    <div className="text-sm text-gray-500">
                      {formatDateTime(item.created_at)}
                    </div>
                  </div>
                  <div className="text-sm text-gray-600 line-clamp-3">
                    {item.analysis_text.substring(0, 200)}...
                  </div>
                </div>
              ))}
            </div>

            {/* Botão para carregar mais */}
            <div className="mt-6 text-center">
              <button
                onClick={loadMoreHistory}
                disabled={isLoadingHistory}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 transition-colors"
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

        {/* Estado vazio */}
        {!currentAnalysis && !isAnalyzing && !error && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Activity className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhuma análise realizada
            </h3>
            <p className="text-gray-600 mb-4">
              Clique em "Analisar Agora" para gerar a primeira análise da partida.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
} 