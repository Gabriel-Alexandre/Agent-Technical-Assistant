-- =====================================================
-- SCRIPT DE CRIAÇÃO DO BANCO DE DADOS
-- Sistema de Coleta de Dados do SofaScore
-- Gerado automaticamente pelo DatabaseService
-- =====================================================

-- Criar extensão UUID se não existir
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABELAS
-- =====================================================

-- Tabela principal para dados de partidas
CREATE TABLE IF NOT EXISTS match_data (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    match_id VARCHAR(50) NOT NULL,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    full_data JSONB NOT NULL,
    simplified_data JSONB,
    analysis_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para armazenar links filtrados
CREATE TABLE IF NOT EXISTS filtered_links (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    collection_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    source_file VARCHAR(255),
    pattern_used VARCHAR(100),
    total_links INTEGER DEFAULT 0,
    links_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para informações das partidas
CREATE TABLE IF NOT EXISTS match_info (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    match_id VARCHAR(50) NOT NULL UNIQUE,
    url_complete VARCHAR(500) NOT NULL,
    url_slug VARCHAR(300),
    title VARCHAR(200),
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    tournament VARCHAR(100),
    match_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para análises de screenshots
CREATE TABLE IF NOT EXISTS screenshot_analysis (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    match_id VARCHAR(50) NOT NULL,
    match_identifier VARCHAR(300) NOT NULL,
    match_url VARCHAR(500) NOT NULL,
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    analysis_text TEXT NOT NULL,
    analysis_type VARCHAR(50) DEFAULT 'context_based',
    analysis_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ÍNDICES PARA PERFORMANCE
-- =====================================================

-- Índices para match_data
CREATE INDEX IF NOT EXISTS idx_match_data_match_id ON match_data(match_id);
CREATE INDEX IF NOT EXISTS idx_match_data_collected_at ON match_data(collected_at);
CREATE INDEX IF NOT EXISTS idx_match_data_created_at ON match_data(created_at);

-- Índices para filtered_links
CREATE INDEX IF NOT EXISTS idx_filtered_links_timestamp ON filtered_links(collection_timestamp);
CREATE INDEX IF NOT EXISTS idx_filtered_links_created_at ON filtered_links(created_at);

-- Índices para match_info
CREATE INDEX IF NOT EXISTS idx_match_info_match_id ON match_info(match_id);
CREATE INDEX IF NOT EXISTS idx_match_info_status ON match_info(status);
CREATE INDEX IF NOT EXISTS idx_match_info_is_active ON match_info(is_active);
CREATE INDEX IF NOT EXISTS idx_match_info_match_date ON match_info(match_date);

-- Índices para screenshot_analysis
CREATE INDEX IF NOT EXISTS idx_screenshot_analysis_match_id ON screenshot_analysis(match_id);
CREATE INDEX IF NOT EXISTS idx_screenshot_analysis_created_at ON screenshot_analysis(created_at);
CREATE INDEX IF NOT EXISTS idx_screenshot_analysis_analysis_type ON screenshot_analysis(analysis_type);

-- =====================================================
-- SEGURANÇA - ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Habilitar RLS para todas as tabelas
ALTER TABLE match_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE filtered_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE match_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE screenshot_analysis ENABLE ROW LEVEL SECURITY;

-- Políticas RLS para permitir acesso público (sem autenticação de usuário)
DO $$
BEGIN
    -- Política para match_data
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename = 'match_data' 
        AND policyname = 'Allow public access'
    ) THEN
        CREATE POLICY "Allow public access" ON match_data 
        FOR ALL USING (true) WITH CHECK (true);
    END IF;
    
    -- Política para filtered_links
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename = 'filtered_links' 
        AND policyname = 'Allow public access'
    ) THEN
        CREATE POLICY "Allow public access" ON filtered_links 
        FOR ALL USING (true) WITH CHECK (true);
    END IF;
    
    -- Política para match_info
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename = 'match_info' 
        AND policyname = 'Allow public access'
    ) THEN
        CREATE POLICY "Allow public access" ON match_info 
        FOR ALL USING (true) WITH CHECK (true);
    END IF;
    
    -- Política para screenshot_analysis
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename = 'screenshot_analysis' 
        AND policyname = 'Allow public access'
    ) THEN
        CREATE POLICY "Allow public access" ON screenshot_analysis 
        FOR ALL USING (true) WITH CHECK (true);
    END IF;
END$$;

-- =====================================================
-- TRIGGERS PARA ATUALIZAÇÃO AUTOMÁTICA
-- =====================================================

-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar triggers para todas as tabelas
DROP TRIGGER IF EXISTS update_match_data_updated_at ON match_data;
CREATE TRIGGER update_match_data_updated_at
    BEFORE UPDATE ON match_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
DROP TRIGGER IF EXISTS update_filtered_links_updated_at ON filtered_links;
CREATE TRIGGER update_filtered_links_updated_at
    BEFORE UPDATE ON filtered_links
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
DROP TRIGGER IF EXISTS update_match_info_updated_at ON match_info;
CREATE TRIGGER update_match_info_updated_at
    BEFORE UPDATE ON match_info
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
DROP TRIGGER IF EXISTS update_screenshot_analysis_updated_at ON screenshot_analysis;
CREATE TRIGGER update_screenshot_analysis_updated_at
    BEFORE UPDATE ON screenshot_analysis
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS ÚTEIS (OPCIONAL)
-- =====================================================

-- View para estatísticas gerais
CREATE OR REPLACE VIEW database_stats AS
SELECT 
    'match_data' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT match_id) as unique_matches,
    MIN(created_at) as first_record,
    MAX(created_at) as last_record
FROM match_data
UNION ALL
SELECT 
    'filtered_links' as table_name,
    COUNT(*) as total_records,
    SUM(total_links) as unique_matches,
    MIN(created_at) as first_record,
    MAX(created_at) as last_record
FROM filtered_links
UNION ALL
SELECT 
    'match_info' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE is_active = true) as unique_matches,
    MIN(created_at) as first_record,
    MAX(created_at) as last_record
FROM match_info;

-- View para partidas ativas com dados
CREATE OR REPLACE VIEW active_matches_with_data AS
SELECT 
    mi.match_id,
    mi.title,
    mi.home_team,
    mi.away_team,
    mi.tournament,
    mi.status,
    mi.match_date,
    mi.url_complete,
    COUNT(md.id) as data_collections,
    MAX(md.collected_at) as last_data_collection
FROM match_info mi
LEFT JOIN match_data md ON mi.match_id = md.match_id
WHERE mi.is_active = true
GROUP BY mi.id, mi.match_id, mi.title, mi.home_team, mi.away_team, 
         mi.tournament, mi.status, mi.match_date, mi.url_complete
ORDER BY mi.created_at DESC;

-- =====================================================
-- COMENTÁRIOS FINAIS
-- =====================================================

-- Script gerado automaticamente
-- Para executar: Cole este conteúdo no SQL Editor do Supabase
-- Todas as operações são seguras (IF NOT EXISTS)
-- 
-- Tabelas criadas:
-- 1. match_data - Dados completos das partidas
-- 2. filtered_links - Links filtrados por timestamp
-- 3. match_info - Informações básicas das partidas
--
-- Recursos incluídos:
-- - Índices para performance
-- - RLS para segurança
-- - Triggers para auditoria
-- - Views para consultas úteis
