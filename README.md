# 🤖⚽ Agent Technical Assistant

**Sistema Inteligente de Análise Técnica de Futebol em Tempo Real**

Um assistente técnico automatizado que coleta dados de partidas de futebol do SofaScore e fornece análises táticas especializadas usando Inteligência Artificial.

## 📋 Visão Geral

O **Agent Technical Assistant** é uma solução completa para análise técnica de futebol que combina:
- **Scrapping inteligente** de dados do SofaScore
- **Interface web moderna** para visualização das partidas
- **Análise tática especializada** usando GPT-4o-mini
- **Monitoramento em tempo real** de partidas de futebol

## 🏗️ Arquitetura do Sistema

```
Agent-Technical-Assistant/
├── Scrapper/          # 🐍 Backend Python (FastAPI)
│   ├── main.py        # API principal
│   ├── services.py    # Serviços de coleta
│   ├── models.py      # Modelos de dados
│   └── important_scripts/
│       ├── agent-assitant.py     # Assistente de análise tática
│       ├── coletor_playwright.py # Coleta com Playwright
│       └── get-print-from-match.py # Captura de screenshots
└── web/               # ⚛️ Frontend Next.js
    ├── src/app/       # Páginas da aplicação
    ├── src/components/ # Componentes React
    └── src/services/  # Integração com API
```

## ✨ Principais Funcionalidades

### 🎯 Coleta de Dados
- **Extração automatizada** de dados do SofaScore usando Playwright
- **Filtro inteligente** para partidas de futebol (exclui outros esportes)
- **Dados em tempo real**: placares, times, status, tempo de jogo
- **Screenshots automáticos** das páginas de partidas

### 📊 Interface Web
- **Dashboard moderno** com visualização das partidas
- **Filtros avançados** por status, times, competições
- **Paginação** e busca inteligente
- **Atualização em tempo real** dos dados

### 🧠 Análise Técnica com IA
- **Análise tática especializada** usando GPT-4o-mini
- **Sugestões específicas** para cada time
- **Avaliação de momentum** e situação da partida
- **Recomendações baseadas em dados reais**

### 💾 Armazenamento
- **Banco de dados Supabase** para persistência
- **Histórico completo** de partidas e análises
- **Backup automático** de screenshots

## 🚀 Tecnologias Utilizadas

### Backend (Scrapper/)
- **FastAPI** - Framework web moderno para Python
- **Playwright** - Automação web para scrapping
- **OpenAI GPT-4o-mini** - Análise tática com IA
- **Supabase** - Banco de dados PostgreSQL
- **SQLAlchemy** - ORM para Python
- **Asyncio** - Programação assíncrona

### Frontend (web/)
- **Next.js 15** - Framework React
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Estilização moderna
- **Lucide React** - Ícones
- **Axios** - Cliente HTTP

## 📦 Instalação e Configuração

### Pré-requisitos
- **Python 3.8+**
- **Node.js 18+**
- **Docker** (opcional)

### 1. Backend Setup

```bash
cd Scrapper/

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp env_example.txt .env
# Editar .env com suas credenciais
```

### 2. Frontend Setup

```bash
cd web/

# Instalar dependências
npm install
# ou
yarn install
```

### 3. Configuração do Banco de Dados

```bash
# Executar script de configuração do banco
cd Scrapper/
python database_service.py
```

## 🔧 Configuração das Variáveis de Ambiente

Crie um arquivo `.env` na pasta `Scrapper/` com:

```env
# OpenAI (para análise técnica)
OPENAI_API_KEY=seu_token_openai

# Supabase (banco de dados)
SUPABASE_URL=sua_url_supabase
SUPABASE_KEY=sua_chave_supabase

# Configurações opcionais
PLAYWRIGHT_HEADLESS=true
API_PORT=8000
```

## 🚀 Como Executar

### Desenvolvimento

#### 1. Iniciar Backend
```bash
cd Scrapper/
python main.py
# API estará disponível em http://localhost:8000
```

#### 2. Iniciar Frontend
```bash
cd web/
npm run dev
# Interface estará disponível em http://localhost:3000
```

### Produção com Docker

```bash
# Backend
cd Scrapper/
docker-compose up -d

# Frontend
cd web/
docker build -t agent-web .
docker run -p 3000:3000 agent-web
```

## 📖 Como Usar

### 1. Coleta de Partidas
- Acesse a interface web em `http://localhost:3000`
- Clique em **"Atualizar Dados"** para coletar partidas atuais
- Visualize as partidas com filtros por status e times

### 2. Análise Técnica
- Clique em **"Análise"** em qualquer partida
- O sistema coletará dados em tempo real
- Receberá análise tática especializada com sugestões

### 3. Monitoramento
- Use a atualização automática para monitorar partidas
- Visualize histórico de análises
- Capture screenshots das partidas

## 🔍 Endpoints da API

### Coleta de Dados
- `GET /` - Status da API
- `POST /sofascore/collect-links` - Coletar partidas atuais
- `GET /sofascore/latest-links` - Última coleta salva

### Análise de Partidas
- `POST /match/{match_id}/screenshot-analysis` - Análise técnica
- `GET /match/{match_id}/screenshot-analyses` - Histórico de análises
- `POST /match/{match_id}/screenshot` - Capturar screenshot

### Monitoramento
- `GET /health` - Status do sistema
- `GET /test/database` - Teste de conexão com banco

## 🎯 Casos de Uso

### Para Analistas Técnicos
- **Análise em tempo real** de partidas em andamento
- **Sugestões táticas** baseadas em dados atuais
- **Monitoramento** de múltiplas partidas simultaneamente

### Para Apostadores Esportivos
- **Dados atualizados** sobre o status das partidas
- **Análise de momentum** e situação do jogo
- **Informações precisas** sobre placares e tempo

### Para Desenvolvedores
- **API completa** para integração
- **Dados estruturados** em JSON
- **Sistema escalável** e bem documentado

## 🔒 Limitações e Avisos

- ⚠️ **Respeite os termos de uso** do SofaScore
- ⚠️ **Use responsavelmente** para não sobrecarregar o site
- ⚠️ **Configure delays** adequados entre requisições
- ⚠️ **Apenas para fins educacionais** e análise pessoal

## 🤝 Contribuindo

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

## 📝 Licença

Este projeto é licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **SofaScore** pelos dados de futebol
- **OpenAI** pela tecnologia de IA
- **Supabase** pela infraestrutura de banco de dados
- **Playwright** pela automação web

## 📞 Suporte

Para dúvidas ou problemas:
- 🐛 **Issues**: [GitHub Issues](https://github.com/seu-usuario/Agent-Technical-Assistant/issues)
- 📧 **Email**: suporte@exemplo.com
- 💬 **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/Agent-Technical-Assistant/discussions)

---

<div align="center">

**Desenvolvido com ❤️ para análise técnica de futebol**

[⚽ Ver Demo](http://localhost:3000) • [📚 Documentação](./docs/) • [🚀 Deployment](./docs/deployment.md)

</div> 