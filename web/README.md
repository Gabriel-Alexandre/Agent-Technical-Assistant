# Assistente Técnico de Futebol - Interface Web

Interface web moderna para o sistema de análise técnica de futebol em tempo real.

## 🚀 Tecnologias

- **Next.js 15** - Framework React com App Router
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Estilização utilitária
- **Lucide React** - Ícones modernos
- **Axios** - Cliente HTTP
- **date-fns** - Manipulação de datas

## 📋 Funcionalidades

### 🏠 Página Principal - Partidas ao Vivo
- Lista de partidas em tempo real
- Botões para capturar screenshots
- Botões para gerar análises técnicas
- Status de conexão com a API
- Estatísticas em tempo real

### 📊 Página de Histórico
- Visualização de todas as análises geradas
- Sistema de busca e filtros
- Ordenação por data ou time
- Estatísticas de análises
- Expansão/contração de conteúdo

## 🛠️ Instalação e Execução

### Pré-requisitos
- Node.js 18+ 
- npm ou yarn

### Passos

1. **Instalar dependências:**
   ```bash
   npm install
   ```

2. **Configurar variáveis de ambiente:**
   ```bash
   # Criar arquivo .env.local
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

3. **Executar em modo desenvolvimento:**
   ```bash
   npm run dev
   ```

4. **Acessar a aplicação:**
   ```
   http://localhost:3000
   ```

## 🔗 Integração com API

A aplicação consome as seguintes rotas da API FastAPI:

### Rotas Ativas
- `POST /sofascore/collect-links` - Coletar links de partidas
- `GET /screenshot-analyses` - Listar todas as análises
- `GET /match/{match_id}/screenshot-analyses` - Análises de uma partida
- `POST /match/{match_identifier}/screenshot` - Capturar screenshot
- `POST /match/{match_identifier}/screenshot-analysis` - Gerar análise

### Configuração da API
Por padrão, a aplicação tenta conectar com a API em `http://localhost:8000`. 
Para alterar, modifique a variável `NEXT_PUBLIC_API_URL` no arquivo `.env.local`.

## 📱 Modo de Desenvolvimento

A aplicação funciona com dados mock quando a API não está disponível:

- **Partidas Mock**: 5 partidas de exemplo com times famosos
- **Análises Mock**: 5 análises técnicas detalhadas
- **Simulação de Loading**: Estados de carregamento realistas
- **Tratamento de Erros**: Fallbacks para quando a API está offline

## 🎨 Design System

### Cores Principais
- **Azul**: `#2563eb` - Ações primárias
- **Verde**: `#16a34a` - Sucesso e análises
- **Cinza**: `#6b7280` - Textos secundários
- **Vermelho**: `#dc2626` - Erros e alertas

### Componentes
- **Layout**: Header, navegação e footer
- **MatchCard**: Card de partida com ações
- **AnalysisCard**: Card de análise com expansão
- **Estados**: Loading, vazio, erro

## 📦 Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev

# Build de produção
npm run build

# Executar build
npm start

# Linting
npm run lint
```

## 🔄 Estados da Aplicação

### Conectado à API
- Dados reais do SofaScore
- Funcionalidades completas
- Atualizações em tempo real

### Modo Mock (Desenvolvimento)
- Dados de exemplo
- Interface totalmente funcional
- Simulação de comportamentos da API

## 🚀 Deploy

### Vercel (Recomendado)
```bash
npm install -g vercel
vercel
```

### Build Manual
```bash
npm run build
npm start
```

## 📝 Estrutura do Projeto

```
web/
├── src/
│   ├── app/                 # App Router do Next.js
│   │   ├── page.tsx         # Página principal
│   │   ├── historico/       # Página de histórico
│   │   └── layout.tsx       # Layout raiz
│   ├── components/          # Componentes reutilizáveis
│   │   ├── Layout.tsx       # Layout principal
│   │   ├── MatchCard.tsx    # Card de partida
│   │   └── AnalysisCard.tsx # Card de análise
│   ├── services/            # Serviços de API
│   │   └── api.ts           # Cliente da API
│   ├── types/               # Tipos TypeScript
│   │   └── api.ts           # Tipos da API
│   └── data/                # Dados mock
│       └── mockData.ts      # Dados de exemplo
├── public/                  # Arquivos estáticos
├── package.json             # Dependências
└── tailwind.config.ts       # Configuração do Tailwind
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
