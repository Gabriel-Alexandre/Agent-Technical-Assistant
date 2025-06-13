// Tipos para as respostas da API SofaScore

export interface ApiResponse {
  success: boolean;
  message: string;
  timestamp: string;
}

export interface MatchLink {
  url: string;
  text: string;
  title?: string;
  match_id: string;
  href_original: string;
  sport?: string;
}

// Novo tipo para a resposta da API de latest-links
export interface LatestLinksResponse extends ApiResponse {
  data: {
    filtered_links: MatchLink[];
    statistics: {
      total_filtered_links: number;
      unique_match_ids: number;
      links_with_text: number;
      links_with_title: number;
    };
    sample_links: MatchLink[];
  };
  collection_info: {
    id: string;
    collection_timestamp: string;
    source_file: string;
    pattern_used: string;
    total_links: number;
    created_at: string;
    updated_at: string;
  };
}

export interface LinksCollectionResponse extends ApiResponse {
  data: MatchLink[];
  total_links: number;
  filtered_links: number;
}

export interface MatchInfo {
  match_id: string;
  home_team: string;
  away_team: string;
  match_url: string;
}

export interface ScreenshotAnalysis {
  id: string;
  match_id: string;
  home_team: string;
  away_team: string;
  match_url: string;
  analysis_text: string;
  screenshot_filename?: string;
  created_at: string;
  updated_at: string;
}

export interface ScreenshotAnalysisListResponse extends ApiResponse {
  data: ScreenshotAnalysis[];
  total_analyses: number;
}

export interface ScreenshotAnalysisDetailResponse extends ApiResponse {
  analysis_data: ScreenshotAnalysis;
  match_info: MatchInfo;
}

export interface SystemStatus {
  screenshots: string;
  visual_analysis: string;
  data_collection: string;
  database: string;
}

export interface ApiStatusResponse {
  message: string;
  version: string;
  status: string;
  timestamp: string;
  active_endpoints: Record<string, string>;
  disabled_endpoints: Record<string, string>;
  system_status: SystemStatus;
} 