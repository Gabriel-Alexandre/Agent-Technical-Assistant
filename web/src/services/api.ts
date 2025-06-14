import axios from 'axios';
import {
  LinksCollectionResponse,
  ScreenshotAnalysisListResponse,
  ApiStatusResponse,
  LatestLinksResponse,
  CollectLinksDetailedResponse
} from '@/types/api';

// URL base da API - pode ser configurada via variável de ambiente
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 segundos para operações normais
  headers: {
    'Content-Type': 'application/json',
  },
});

// API específica para operações de coleta (timeout maior)
const apiCollect = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutos para coleta
  headers: {
    'Content-Type': 'application/json',
  },
});

export class ApiService {
  // Obter status da API
  static async getApiStatus(): Promise<ApiStatusResponse> {
    const response = await api.get('/');
    return response.data;
  }

  // Obter links mais recentes do SofaScore
  static async getLatestLinks(): Promise<LatestLinksResponse> {
    const response = await api.get('/sofascore/latest-links');
    return response.data;
  }

  // Coletar links de partidas do SofaScore
  static async collectLinks(): Promise<LinksCollectionResponse> {
    const response = await apiCollect.post('/sofascore/collect-links');
    return response.data;
  }

  // Coletar links de partidas detalhadas do SofaScore
  static async collectDetailedLinks(): Promise<CollectLinksDetailedResponse> {
    const response = await apiCollect.post('/sofascore/collect-links');
    return response.data;
  }

  // Obter todas as análises de screenshot
  static async getAllScreenshotAnalyses(limit: number = 50): Promise<ScreenshotAnalysisListResponse> {
    const response = await api.get(`/screenshot-analyses?limit=${limit}`);
    return response.data;
  }

  // Obter análises de screenshot de uma partida específica
  static async getMatchScreenshotAnalyses(matchId: string, limit: number = 10): Promise<ScreenshotAnalysisListResponse> {
    const response = await api.get(`/match/${matchId}/screenshot-analyses?limit=${limit}`);
    return response.data;
  }

  // Gerar análise de screenshot para uma partida
  static async generateScreenshotAnalysis(matchIdentifier: string) {
    const response = await api.post(`/match/${encodeURIComponent(matchIdentifier)}/screenshot-analysis`);
    return response.data;
  }

  // Capturar screenshot de uma partida
  static async captureScreenshot(matchIdentifier: string) {
    const response = await api.post(`/match/${encodeURIComponent(matchIdentifier)}/screenshot`);
    return response.data;
  }
}

export default ApiService; 