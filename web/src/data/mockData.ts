import { MatchLink, ScreenshotAnalysis } from '@/types/api';

// Mock data para partidas ao vivo
export const mockLiveMatches: MatchLink[] = [
  {
    url: 'https://www.sofascore.com/pt/football/match/real-madrid-barcelona/abc123#id:12345678',
    text: 'Real Madrid vs Barcelona',
    title: 'El Clásico - La Liga',
    match_id: '12345678',
    created_at: '2024-06-12T20:30:00Z'
  },
  {
    url: 'https://www.sofascore.com/pt/football/match/manchester-city-liverpool/def456#id:87654321',
    text: 'Manchester City vs Liverpool',
    title: 'Premier League',
    match_id: '87654321',
    created_at: '2024-06-12T19:45:00Z'
  },
  {
    url: 'https://www.sofascore.com/pt/football/match/psg-marseille/ghi789#id:11223344',
    text: 'PSG vs Marseille',
    title: 'Le Classique - Ligue 1',
    match_id: '11223344',
    created_at: '2024-06-12T21:00:00Z'
  },
  {
    url: 'https://www.sofascore.com/pt/football/match/bayern-dortmund/jkl012#id:55667788',
    text: 'Bayern München vs Borussia Dortmund',
    title: 'Der Klassiker - Bundesliga',
    match_id: '55667788',
    created_at: '2024-06-12T18:30:00Z'
  },
  {
    url: 'https://www.sofascore.com/pt/football/match/juventus-inter/mno345#id:99887766',
    text: 'Juventus vs Inter Milan',
    title: 'Derby d\'Italia - Serie A',
    match_id: '99887766',
    created_at: '2024-06-12T20:00:00Z'
  }
];

// Mock data para análises de screenshot
export const mockScreenshotAnalyses: ScreenshotAnalysis[] = [
  {
    id: '1',
    match_id: '12345678',
    home_team: 'Real Madrid',
    away_team: 'Barcelona',
    match_url: 'https://www.sofascore.com/pt/football/match/real-madrid-barcelona/abc123#id:12345678',
    analysis_text: `🏆 **ANÁLISE TÉCNICA - EL CLÁSICO**

📊 **Situação Atual:**
- Real Madrid 2-1 Barcelona (75' minuto)
- Partida equilibrada com intensidade máxima
- Ambos os times buscando o gol da vitória

⚽ **Contexto Tático:**
- Real Madrid adotando postura mais defensiva após abrir 2-0
- Barcelona pressionando com posse de bola alta (68%)
- Jogo concentrado no meio-campo com poucas chances claras

🎯 **Recomendações Técnicas:**

**Para o Real Madrid:**
- Manter compactação defensiva
- Explorar contra-ataques pelas laterais
- Substituições para ganhar tempo e energia

**Para o Barcelona:**
- Aumentar velocidade de circulação de bola
- Buscar jogadas pelos flancos
- Pressão alta para forçar erros

⚠️ **Alertas Críticos:**
- Cartões amarelos acumulando (risco de expulsões)
- Fadiga física evidente nos dois times
- Tensão crescente - possíveis confrontos

📈 **Previsão Tática:**
Partida deve se manter equilibrada com Barcelona pressionando e Real Madrid explorando contra-ataques. Decisão provável nos últimos 10 minutos.`,
    screenshot_filename: 'real_madrid_barcelona_20240612_203000.png',
    created_at: '2024-06-12T20:30:00Z',
    updated_at: '2024-06-12T20:30:00Z'
  },
  {
    id: '2',
    match_id: '87654321',
    home_team: 'Manchester City',
    away_team: 'Liverpool',
    match_url: 'https://www.sofascore.com/pt/football/match/manchester-city-liverpool/def456#id:87654321',
    analysis_text: `⚽ **ANÁLISE TÉCNICA - PREMIER LEAGUE**

📊 **Situação Atual:**
- Manchester City 1-1 Liverpool (58' minuto)
- Jogo de alta intensidade e qualidade técnica
- Ambos os times criando oportunidades

⚽ **Contexto Tático:**
- City controlando posse (62%) mas Liverpool eficiente
- Pressing alto de ambos os lados
- Meio-campo disputado com muitas recuperações

🎯 **Recomendações Técnicas:**

**Para o Manchester City:**
- Explorar espaços pelas costas da defesa
- Aumentar participação dos laterais no ataque
- Paciência na construção das jogadas

**Para o Liverpool:**
- Manter intensidade no pressing
- Aproveitar transições rápidas
- Explorar velocidade dos pontas

⚠️ **Alertas Críticos:**
- Ritmo físico muito alto (risco de lesões)
- Várias faltas táticas cometidas
- Goleiros sendo decisivos

📈 **Previsão Tática:**
Jogo deve continuar equilibrado. Quem conseguir manter a intensidade física por mais tempo terá vantagem decisiva.`,
    screenshot_filename: 'manchester_city_liverpool_20240612_194500.png',
    created_at: '2024-06-12T19:45:00Z',
    updated_at: '2024-06-12T19:45:00Z'
  },
  {
    id: '3',
    match_id: '11223344',
    home_team: 'PSG',
    away_team: 'Marseille',
    match_url: 'https://www.sofascore.com/pt/football/match/psg-marseille/ghi789#id:11223344',
    analysis_text: `🇫🇷 **ANÁLISE TÉCNICA - LE CLASSIQUE**

📊 **Situação Atual:**
- PSG 3-0 Marseille (42' minuto)
- Domínio total do PSG no primeiro tempo
- Marseille tentando se reorganizar

⚽ **Contexto Tático:**
- PSG explorando velocidade no ataque
- Marseille com dificuldades defensivas
- Diferença técnica sendo determinante

🎯 **Recomendações Técnicas:**

**Para o PSG:**
- Manter intensidade para ampliar vantagem
- Rotacionar jogadores para segundo tempo
- Controlar ritmo do jogo

**Para o Marseille:**
- Mudança tática urgente no intervalo
- Pressionar saída de bola do PSG
- Buscar diminuir diferença antes do intervalo

⚠️ **Alertas Críticos:**
- Marseille desorganizado defensivamente
- PSG pode relaxar com vantagem
- Torcida pressionando time visitante

📈 **Previsão Tática:**
PSG deve administrar vantagem no segundo tempo. Marseille precisa de mudanças drásticas para reagir.`,
    created_at: '2024-06-12T21:00:00Z',
    updated_at: '2024-06-12T21:00:00Z'
  },
  {
    id: '4',
    match_id: '55667788',
    home_team: 'Bayern München',
    away_team: 'Borussia Dortmund',
    match_url: 'https://www.sofascore.com/pt/football/match/bayern-dortmund/jkl012#id:55667788',
    analysis_text: `🇩🇪 **ANÁLISE TÉCNICA - DER KLASSIKER**

📊 **Situação Atual:**
- Bayern München 1-2 Borussia Dortmund (67' minuto)
- Dortmund surpreendendo com eficiência
- Bayern pressionando em busca do empate

⚽ **Contexto Tático:**
- Dortmund apostando em contra-ataques letais
- Bayern com posse mas sem penetração
- Jogo físico e disputado no meio-campo

🎯 **Recomendações Técnicas:**

**Para o Bayern München:**
- Aumentar cruzamentos na área
- Pressionar saída de bola do Dortmund
- Entradas de jogadores ofensivos

**Para o Borussia Dortmund:**
- Manter organização defensiva
- Explorar espaços no contra-ataque
- Administrar vantagem com inteligência

⚠️ **Alertas Críticos:**
- Bayern desesperado pode se expor
- Dortmund cansando fisicamente
- Árbitro sendo permissivo com faltas

📈 **Previsão Tática:**
Últimos 20 minutos serão decisivos. Bayern deve pressionar mais e Dortmund precisa resistir.`,
    created_at: '2024-06-12T18:30:00Z',
    updated_at: '2024-06-12T18:30:00Z'
  },
  {
    id: '5',
    match_id: '99887766',
    home_team: 'Juventus',
    away_team: 'Inter Milan',
    match_url: 'https://www.sofascore.com/pt/football/match/juventus-inter/mno345#id:99887766',
    analysis_text: `🇮🇹 **ANÁLISE TÉCNICA - DERBY D'ITALIA**

📊 **Situação Atual:**
- Juventus 0-0 Inter Milan (23' minuto)
- Início cauteloso de ambos os times
- Poucas oportunidades criadas

⚽ **Contexto Tático:**
- Ambos priorizando não sofrer gols
- Meio-campo muito disputado
- Defesas bem organizadas

🎯 **Recomendações Técnicas:**

**Para a Juventus:**
- Aumentar velocidade na saída de bola
- Explorar jogadas pelas laterais
- Pressionar mais a marcação

**Para a Inter Milan:**
- Manter paciência na construção
- Aproveitar bolas paradas
- Explorar velocidade dos atacantes

⚠️ **Alertas Críticos:**
- Jogo muito truncado no meio-campo
- Poucas finalizações até agora
- Tensão típica de derby

📈 **Previsão Tática:**
Jogo deve se abrir mais no segundo tempo. Primeiro gol será crucial para definir a estratégia.`,
    created_at: '2024-06-12T20:00:00Z',
    updated_at: '2024-06-12T20:00:00Z'
  }
]; 