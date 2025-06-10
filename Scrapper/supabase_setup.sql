
-- SQL para criar tabelas no Supabase
-- Execute este código no SQL Editor do Supabase

-- Criar extensão UUID se não existir
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_match_data_match_id ON match_data(match_id);
CREATE INDEX IF NOT EXISTS idx_match_data_collected_at ON match_data(collected_at);
CREATE INDEX IF NOT EXISTS idx_match_data_created_at ON match_data(created_at);

-- Habilitar RLS (Row Level Security)
ALTER TABLE match_data ENABLE ROW LEVEL SECURITY;

-- Política RLS para permitir acesso público (sem autenticação de usuário)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename = 'match_data' 
        AND policyname = 'Allow public access'
    ) THEN
        CREATE POLICY "Allow public access" ON match_data 
        FOR ALL USING (true) WITH CHECK (true);
    END IF;
END$$;

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_match_data_updated_at ON match_data;
CREATE TRIGGER update_match_data_updated_at
    BEFORE UPDATE ON match_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
