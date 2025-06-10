# 🏆 API de Coleta de Dados do SofaScore

Esta API transforma os scripts de coleta de dados em uma interface REST completa para análise técnica de futebol em tempo real.

## 🚀 Configuração Inicial

### 1. Ativar Ambiente Virtual
```bash
cd Scrapper
.\venv\Scripts\Activate.ps1
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na pasta `Scrapper` com:
```env
SUPABASE_URL=sua_url_supabase
SUPABASE_ANON_KEY=sua_chave_anonima_supabase
OPENAI_API_KEY=sua_chave_openai
```

### 4. Configurar Banco de Dados
Execute o script de configuração:
```bash
python setup_api.py
```

**IMPORTANTE**: Execute o SQL gerado (`supabase_setup.sql`) no SQL Editor do Supabase.

### 5. Iniciar API
```bash
python main.py
```

A API estará disponível em: `http://localhost:8000`
Documentação Swagger: `http://localhost:8000/docs`

## 📚 Endpoints Disponíveis

### 🏠 Status da API
- **GET** `/` - Status geral da API
- **GET** `/health` - Verificação de saúde dos serviços

### 📊 Coleta de Dados

#### 1. Dados Completos
**POST** `/match/{match_id}/full-data`

Coleta todos os dados disponíveis do SofaScore para uma partida.

**Exemplo:**
```bash
curl -X POST "http://localhost:8000/match/11161648/full-data"
```

**Dados coletados:**
- ✅ Informações básicas (times, placar, status)
- ✅ Estatísticas detalhadas
- ✅ Timeline de eventos
- ✅ Escalações e formações
- ✅ Mapa de chutes (shotmap)
- ✅ Estatísticas de jogadores

#### 2. Dados Simplificados
**POST** `/match/{match_id}/simplified-data`

Coleta e simplifica dados, extraindo apenas informações relevantes.

**Exemplo:**
```bash
curl -X POST "http://localhost:8000/match/11161648/simplified-data"
```

**Dados simplificados:**
- 🎯 Resumo da partida
- 📈 Estatísticas principais categorizadas
- ⚽ Eventos importantes (gols, cartões, substituições)
- 🔄 Configuração tática
- 🎯 Análise de chutes

#### 3. Análise Completa com IA
**POST** `/match/{match_id}/analysis`

Gera análise técnica completa usando GPT-4o-mini.

**Exemplo:**
```bash
curl -X POST "http://localhost:8000/match/11161648/analysis"
```

**Inclui:**
- 🤖 Situação tática atual
- 🔍 Análise crítica de pontos-chave
- ⚡ Sugestões táticas prioritárias
- 🚨 Alertas críticos
- 📈 Previsão tática

### 📚 Histórico
**GET** `/match/{match_id}/history?limit=10`

Recupera histórico de coletas de uma partida.

## 🗄️ Estrutura do Banco de Dados

### Tabela: `match_data`
```sql
CREATE TABLE match_data (
    id UUID PRIMARY KEY,
    match_id VARCHAR(50) NOT NULL,
    collected_at TIMESTAMP WITH TIME ZONE,
    full_data JSONB NOT NULL,
    simplified_data JSONB,
    analysis_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**Características:**
- ✅ Suporte a múltiplas coletas da mesma partida
- ✅ Dados completos em JSONB para flexibilidade
- ✅ Análise de IA armazenada como texto
- ✅ RLS habilitado para segurança
- ✅ Índices para performance otimizada

## 🔄 Uso para Coleta em Tempo Real

Para monitoramento contínuo (coleta a cada 30 segundos):

```python
import asyncio
import aiohttp

async def collect_match_data_loop(match_id, interval=30):
    """Coleta dados em loop para uma partida"""
    async with aiohttp.ClientSession() as session:
        while True:
            # Coletar dados simplificados
            async with session.post(f"http://localhost:8000/match/{match_id}/simplified-data") as resp:
                data = await resp.json()
                print(f"✅ Dados coletados: {data['timestamp']}")
            
            # Aguardar próxima coleta
            await asyncio.sleep(interval)

# Executar
asyncio.run(collect_match_data_loop("11161648"))
```

## 📋 Exemplos de Resposta

### Dados Completos
```json
{
  "success": true,
  "message": "Dados coletados com sucesso",
  "data": {
    "basic_info": {
      "homeTeam": {"name": "Real Madrid", "id": 2829},
      "awayTeam": {"name": "Barcelona", "id": 2817},
      "homeScore": {"current": 2},
      "awayScore": {"current": 1}
    },
    "statistics": [...],
    "timeline": [...],
    "lineups": {...},
    "shotmap": [...]
  },
  "record_id": "uuid-do-registro",
  "timestamp": "2024-01-15T14:30:00"
}
```

### Dados Simplificados
```json
{
  "success": true,
  "message": "Dados simplificados com sucesso",
  "data": {
    "match_summary": {
      "home_team": "Real Madrid",
      "away_team": "Barcelona",
      "score": {"home": 2, "away": 1},
      "status": "2nd Half"
    },
    "key_statistics": {
      "possession": {"Ball possession": {"home": "58%", "away": "42%"}},
      "shots": {"Total shots": {"home": "12", "away": "8"}}
    },
    "events_timeline": {
      "goals": [
        {"time": 25, "team": "home", "player": "Benzema", "assist": "Modric"}
      ]
    }
  },
  "record_id": "uuid-do-registro",
  "timestamp": "2024-01-15T14:30:00"
}
```

### Análise com IA
```json
{
  "success": true,
  "message": "Análise completa realizada com sucesso",
  "match_data": {...},
  "simplified_data": {...},
  "analysis": "📊 SITUAÇÃO TÁTICA ATUAL\nReal Madrid domina tacticamente com 58% de posse...\n\n🔍 ANÁLISE CRÍTICA\n1. **PRESSÃO**: Barcelona precisa aumentar intensidade...",
  "record_id": "uuid-do-registro",
  "timestamp": "2024-01-15T14:30:00"
}
```

## ⚠️ Limitações e Considerações

### Rate Limiting
- SofaScore pode limitar requisições muito frequentes
- Recomendado: máximo 1 coleta por minuto por partida

### Recursos Necessários
- **Playwright**: Para coleta de dados (navegador)
- **OpenAI API**: Para análise técnica (opcional)
- **Supabase**: Para persistência de dados

### Performance
- Coleta completa: ~10-15 segundos
- Dados simplificados: ~8-12 segundos
- Análise com IA: +5-10 segundos adicionais

## 🛠️ Troubleshooting

### Erro: "Assistente técnico não disponível"
- Verifique se `OPENAI_API_KEY` está configurada no `.env`

### Erro: "Falha na coleta de dados"
- Verifique conexão com internet
- Match ID pode estar incorreto ou partida não disponível

### Erro: "Tabela não existe"
- Execute o SQL `supabase_setup.sql` no Supabase SQL Editor

### Playwright não funciona
```bash
playwright install chromium
```

## 🔧 Desenvolvimento

### Executar em modo desenvolvimento:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Logs detalhados:
```bash
uvicorn main:app --reload --log-level debug
```

## 📞 Suporte

Para dúvidas sobre:
- **Coleta de dados**: Verifique logs do Playwright
- **Análise IA**: Verifique configuração OpenAI
- **Banco de dados**: Verifique configuração Supabase
- **API**: Verifique documentação Swagger em `/docs` 