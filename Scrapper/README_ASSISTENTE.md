# 🏆 Assistente Técnico de Futebol - Sistema Completo

## 📋 Visão Geral

Sistema automatizado que coleta dados ao vivo do SofaScore, simplifica para análise por IA e fornece sugestões táticas especializadas usando GPT-4o-mini.

## 🚀 Instalação e Configuração

### 1. Instalar Dependências

```bash
pip install openai python-dotenv
```

Ou instalar todas as dependências:
```bash
pip install -r requirements.txt
```

### 2. Configurar API da OpenAI

1. **Obter chave da API**:
   - Acesse: https://platform.openai.com/api-keys
   - Faça login na sua conta OpenAI
   - Clique em "Create new secret key"
   - Copie a chave gerada

2. **Configurar arquivo .env**:
   ```bash
   # Renomear env_example.txt para .env
   cp env_example.txt .env
   
   # Editar .env e adicionar sua chave:
   OPENAI_API_KEY=sua_chave_real_aqui
   ```

## 🔄 Como Usar o Sistema

### Fluxo Completo Automatizado

```bash
# 1. Coletar dados ao vivo (a cada 30s)
python get_game_info.py 13963638

# 2. Analisar com IA (usando dados simplificados)
python agent-assistant.py live_data_simplify/simplified_match_13963638_20250608_144908.json
```

### Coleta Personalizada

```bash
# Coleta única
python get_game_info.py 13963638 30 1

# Coleta a cada 15 segundos por 10 iterações
python get_game_info.py 13963638 15 10

# Coleta contínua a cada 60 segundos
python get_game_info.py 13963638 60
```

## 📂 Estrutura de Arquivos

```
Scrapper/
├── get_game_info.py              # Coletor de dados ao vivo
├── simplify_match_data.py        # Simplificador de dados
├── agent-assistant.py            # Assistente técnico IA
├── live_data/                    # Dados originais completos
│   └── match_*.json              # ~200KB por arquivo
├── live_data_simplify/           # Dados simplificados para IA
│   ├── simplified_match_*.json   # ~10KB por arquivo (95% menor)
│   └── analysis_*.md             # Análises técnicas geradas
├── .env                          # Configurações da API (criar)
└── env_example.txt               # Exemplo de configuração
```

## 🤖 Funcionalidades do Assistente

### Análise Especializada
- **Sistemas Táticos**: Análise de formações e posicionamento
- **Transições**: Pressing, contra-pressing, mudanças de posse
- **Vulnerabilidades**: Identificação de espaços e fraquezas
- **Gestão de Jogo**: Controle de ritmo e momentum
- **Sugestões Específicas**: Ajustes táticos implementáveis

### Formato de Análise
- **Situação Tática Atual**: Resumo do domínio
- **Análise Crítica**: 4 pontos técnicos principais
- **Sugestões Prioritárias**: Para ambos os times
- **Alertas Críticos**: Riscos e oportunidades
- **Previsão Tática**: Evolução esperada do jogo

## 📊 Exemplo de Saída

```
🚀 Iniciando análise técnica de: live_data_simplify/simplified_match_13963638_20250608_144908.json
============================================================
⚽ Racing de Santander 1 x 3 Mirandés
📊 Status: 2nd half
============================================================
🤖 Iniciando análise tática especializada...
✅ Análise concluída!

================================================================================
🏆 ANÁLISE TÉCNICA ESPECIALIZADA
================================================================================

### 📊 SITUAÇÃO TÁTICA ATUAL
Mirandés domina taticamente com superioridade ofensiva clara (12 vs 4 chutes). 
Racing precisa urgentemente ajustar estrutura defensiva e melhorar eficiência.

### 🔍 ANÁLISE CRÍTICA
1. **EFICIÊNCIA OFENSIVA**: Mirandés 3x mais efetivo (12 chutes vs 4)
2. **VULNERABILIDADE DEFENSIVA**: Racing sofre pressão constante
3. **DOMÍNIO TERRITORIAL**: Posse equilibrada mas Mirandés mais perigoso
4. **GESTÃO DE JOGO**: Racing precisa controlar ritmo urgentemente

### ⚡ SUGESTÕES TÁTICAS PRIORITÁRIAS

#### 🏠 Para Racing de Santander:
**URGENTE** - Compactar linhas defensivas e apostar em contra-ataques rápidos

#### 🚌 Para Mirandés:
**MÉDIA** - Manter pressão mas cuidar de transições defensivas

### 🚨 ALERTAS CRÍTICOS
- Racing em risco de colapso defensivo
- Oportunidade de definir o jogo nos próximos 15 minutos

📄 Análise salva em: live_data_simplify/analysis_simplified_match_13963638_20250608_144908_20250608_145123.md

🎯 ANÁLISE CONCLUÍDA!
💡 Use essas informações para tomar decisões táticas informadas.
```

## ⚙️ Configurações Avançadas

### Personalizar Modelo IA
No arquivo `agent-assistant.py`, linha 29:
```python
self.model = "gpt-4o-mini"  # Pode alterar para gpt-4, gpt-3.5-turbo, etc.
```

### Ajustar Temperatura da IA
Linha 147:
```python
temperature=0.3  # 0.0 = mais preciso, 1.0 = mais criativo
```

### Modificar Intervalo de Coleta
```bash
python get_game_info.py 13963638 45  # Coleta a cada 45 segundos
```

## 🔧 Solução de Problemas

### Erro: "OPENAI_API_KEY não encontrada"
- Verificar se arquivo `.env` existe
- Confirmar se a chave está correta no arquivo `.env`
- Verificar se não há espaços extras na chave

### Erro: "Arquivo não encontrado"
- Verificar se o caminho do arquivo está correto
- Usar arquivos da pasta `live_data_simplify/`
- Executar coleta antes da análise

### Erro de conexão com OpenAI
- Verificar conexão com internet
- Confirmar se a chave da API está válida
- Verificar se há créditos na conta OpenAI

## 💡 Dicas de Uso

1. **Monitoramento Contínuo**: Execute coleta em background durante partidas
2. **Análise Comparativa**: Compare análises sequenciais para ver evolução
3. **Timing das Sugestões**: Use análises para decidir substituições e ajustes
4. **Arquivo de Histórico**: Mantenha análises salvas para estudo posterior

## 🎯 Próximos Passos

- Integrar com dashboard em tempo real
- Adicionar análise de padrões históricos
- Implementar alertas automáticos
- Criar relatórios pós-jogo automatizados

---

**Desenvolvido para análise tática profissional de futebol** ⚽🤖 