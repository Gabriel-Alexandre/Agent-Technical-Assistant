"""
Serviço de Banco de Dados - Supabase
Gerencia persistência de dados de partidas no Supabase
"""

import os
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class DatabaseService:
    """Serviço para gerenciar dados no Supabase"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("❌ Variáveis SUPABASE_URL e SUPABASE_ANON_KEY não encontradas no .env")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    async def test_connection(self) -> bool:
        """Testa a conectividade com o Supabase"""
        try:
            # Tentar fazer uma consulta simples
            result = self.client.table('match_info').select('id').limit(1).execute()
            
            if hasattr(result, 'data'):
                return True
            else:
                print("❌ Resposta inesperada do Supabase")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conectividade com Supabase: {e}")
            return False
    
    async def create_tables_if_not_exist(self):
        """Cria tabelas necessárias se não existirem"""
        try:
            # SQL para criar tabelas
            create_tables_sql = """
            SET TIME ZONE 'America/Sao_Paulo';

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
            
            -- Índices para melhor performance
            CREATE INDEX IF NOT EXISTS idx_match_data_match_id ON match_data(match_id);
            CREATE INDEX IF NOT EXISTS idx_match_data_collected_at ON match_data(collected_at);
            CREATE INDEX IF NOT EXISTS idx_match_data_created_at ON match_data(created_at);
            
            CREATE INDEX IF NOT EXISTS idx_filtered_links_timestamp ON filtered_links(collection_timestamp);
            CREATE INDEX IF NOT EXISTS idx_filtered_links_created_at ON filtered_links(created_at);
            
            CREATE INDEX IF NOT EXISTS idx_match_info_match_id ON match_info(match_id);
            CREATE INDEX IF NOT EXISTS idx_match_info_status ON match_info(status);
            CREATE INDEX IF NOT EXISTS idx_match_info_is_active ON match_info(is_active);
            CREATE INDEX IF NOT EXISTS idx_match_info_match_date ON match_info(match_date);
            
            -- Índices para screenshot_analysis
            CREATE INDEX IF NOT EXISTS idx_screenshot_analysis_match_id ON screenshot_analysis(match_id);
            CREATE INDEX IF NOT EXISTS idx_screenshot_analysis_created_at ON screenshot_analysis(created_at);
            CREATE INDEX IF NOT EXISTS idx_screenshot_analysis_analysis_type ON screenshot_analysis(analysis_type);
            
            -- Habilitar RLS (Row Level Security) para todas as tabelas
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
            
            -- Trigger para atualizar updated_at
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
            """
            
            # Executar SQL através de uma function edge (se disponível) ou RPC
            # Como fallback, vamos tentar criar as tabelas via RPC
            print("🔄 Criando tabelas no Supabase...")
            
            # Para Supabase, vamos usar uma abordagem mais simples
            # Verificar se as tabelas existem consultando
            tables_to_check = ['match_data', 'filtered_links', 'match_info', 'screenshot_analysis']
            missing_tables = []
            
            for table_name in tables_to_check:
                try:
                    result = self.client.table(table_name).select('id').limit(1).execute()
                except Exception:
                    missing_tables.append(table_name)
            
            if missing_tables:
                print(f"📝 {len(missing_tables)} tabela(s) precisam ser criadas: {', '.join(missing_tables)}")
                print("📋 Execute o SQL no SQL Editor do Supabase")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar/criar tabelas: {e}")
            return False
    
    async def save_match_data(self, match_id: str, full_data: Dict[str, Any], 
                            simplified_data: Optional[Dict[str, Any]] = None,
                            analysis: Optional[str] = None) -> Optional[str]:
        """Salva dados da partida no Supabase"""
        try:
            record_id = str(uuid.uuid4())
            
            data_to_insert = {
                'id': record_id,
                'match_id': match_id,
                'collected_at': datetime.now().isoformat(),
                'full_data': full_data,
                'simplified_data': simplified_data,
                'analysis_text': analysis
            }
            
            result = self.client.table('match_data').insert(data_to_insert).execute()
            
            if result.data:
                return record_id
            else:
                print(f"❌ Erro ao salvar no Supabase")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")
            return None
    
    async def get_match_data(self, match_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recupera dados de uma partida específica"""
        try:
            result = self.client.table('match_data')\
                .select('*')\
                .eq('match_id', match_id)\
                .order('collected_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar dados: {e}")
            return []
    
    async def get_latest_match_data(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Recupera os dados mais recentes de uma partida"""
        try:
            result = self.client.table('match_data')\
                .select('*')\
                .eq('match_id', match_id)\
                .order('collected_at', desc=True)\
                .limit(1)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"❌ Erro ao buscar dados mais recentes: {e}")
            return None
    
    async def get_match_history(self, match_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recupera o histórico de coletas de uma partida específica"""
        try:
            result = self.client.table('match_data')\
                .select('id, match_id, collected_at, created_at, updated_at')\
                .eq('match_id', match_id)\
                .order('collected_at', desc=True)\
                .limit(limit)\
                .execute()
            
            # Formatar dados para resposta mais amigável
            history = []
            for record in result.data if result.data else []:
                history.append({
                    'record_id': record.get('id'),
                    'collected_at': record.get('collected_at'),
                    'created_at': record.get('created_at'),
                    'updated_at': record.get('updated_at')
                })
            
            return history
            
        except Exception as e:
            print(f"❌ Erro ao buscar histórico: {e}")
            return []
    
    # Métodos para tabela filtered_links
    async def save_filtered_links(self, collection_timestamp: str, source_file: str, 
                                pattern_used: str, links_data: List[Dict[str, Any]]) -> Optional[str]:
        """Salva links filtrados no Supabase"""
        try:
            record_id = str(uuid.uuid4())
            
            data_to_insert = {
                'id': record_id,
                'collection_timestamp': collection_timestamp,
                'source_file': source_file,
                'pattern_used': pattern_used,
                'total_links': len(links_data),
                'links_data': {'filtered_links': links_data}
            }
            
            result = self.client.table('filtered_links').insert(data_to_insert).execute()
            
            if result.data:
                return record_id
            else:
                print(f"❌ Erro ao salvar links filtrados")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao salvar links filtrados: {e}")
            return None
    
    async def get_filtered_links(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Recupera links filtrados mais recentes"""
        try:
            result = self.client.table('filtered_links')\
                .select('*')\
                .order('collection_timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar links filtrados: {e}")
            return []
    
    async def get_latest_filtered_links(self) -> Optional[Dict[str, Any]]:
        """Recupera os links filtrados mais recentes"""
        try:
            result = self.client.table('filtered_links')\
                .select('*')\
                .order('collection_timestamp', desc=True)\
                .limit(1)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"❌ Erro ao buscar links filtrados mais recentes: {e}")
            return None
    
    # Métodos para tabela match_info
    async def save_match_info(self, match_id: str, url_complete: str, url_slug: str = None,
                            title: str = None, home_team: str = None, away_team: str = None,
                            tournament: str = None, match_date: str = None, 
                            status: str = None) -> Optional[str]:
        """Salva informações da partida no Supabase"""
        try:
            # Usar upsert como estratégia principal para evitar conflitos de chave duplicada
            data_to_upsert = {
                'match_id': match_id,
                'url_complete': url_complete,
                'url_slug': url_slug,
                'title': title,
                'home_team': home_team,
                'away_team': away_team,
                'tournament': tournament,
                'match_date': match_date,
                'status': status,
                'is_active': True
            }
            
            # Remover campos None
            data_to_upsert = {k: v for k, v in data_to_upsert.items() if v is not None}
            
            # Usar upsert diretamente (mais eficiente e evita erro de chave duplicada)
            result = self.client.table('match_info').upsert(
                data_to_upsert, 
                on_conflict='match_id'
            ).execute()
            
            if result.data and len(result.data) > 0:
                actual_record_id = result.data[0].get('id')
                return actual_record_id
            else:
                print(f"❌ Upsert retornou dados vazios")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao salvar informações da partida: {e}")
            return None
    
    async def get_match_info(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Recupera informações de uma partida específica"""
        try:
            result = self.client.table('match_info')\
                .select('*')\
                .eq('match_id', match_id)\
                .eq('is_active', True)\
                .limit(1)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"❌ Erro ao buscar informações da partida: {e}")
            return None
    
    async def get_all_active_matches(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Recupera todas as partidas ativas"""
        try:
            result = self.client.table('match_info')\
                .select('*')\
                .eq('is_active', True)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar partidas ativas: {e}")
            return []
    
    async def update_match_status(self, match_id: str, status: str) -> bool:
        """Atualiza o status de uma partida"""
        try:
            result = self.client.table('match_info')\
                .update({'status': status})\
                .eq('match_id', match_id)\
                .execute()
            
            if result.data:
                return True
            else:
                print(f"❌ Erro ao atualizar status da partida")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao atualizar status: {e}")
            return False
    
    async def deactivate_match(self, match_id: str) -> bool:
        """Desativa uma partida (marca como inativa)"""
        try:
            result = self.client.table('match_info')\
                .update({'is_active': False})\
                .eq('match_id', match_id)\
                .execute()
            
            if result.data:
                return True
            else:
                print(f"❌ Erro ao desativar partida")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao desativar partida: {e}")
            return False
    
    # Métodos para tabela screenshot_analysis
    async def save_screenshot_analysis(self, match_id: str, match_identifier: str, match_url: str,
                                     home_team: str = None, away_team: str = None, 
                                     analysis_text: str = None, analysis_type: str = "context_based",
                                     analysis_metadata: Dict[str, Any] = None) -> Optional[str]:
        """Salva análise de screenshot no Supabase"""
        try:
            record_id = str(uuid.uuid4())
            
            data_to_insert = {
                'id': record_id,
                'match_id': match_id,
                'match_identifier': match_identifier,
                'match_url': match_url,
                'home_team': home_team,
                'away_team': away_team,
                'analysis_text': analysis_text,
                'analysis_type': analysis_type,
                'analysis_metadata': analysis_metadata
            }
            
            # Remover campos None
            data_to_insert = {k: v for k, v in data_to_insert.items() if v is not None}
            
            result = self.client.table('screenshot_analysis').insert(data_to_insert).execute()
            
            if result.data:
                return record_id
            else:
                print(f"❌ Erro ao salvar análise de screenshot")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao salvar análise de screenshot: {e}")
            return None
    
    async def get_screenshot_analysis(self, match_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recupera análises de screenshot de uma partida específica"""
        try:
            result = self.client.table('screenshot_analysis')\
                .select('*')\
                .eq('match_id', match_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar análises de screenshot: {e}")
            return []
    
    async def get_latest_screenshot_analysis(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Recupera a análise de screenshot mais recente de uma partida"""
        try:
            result = self.client.table('screenshot_analysis')\
                .select('*')\
                .eq('match_id', match_id)\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"❌ Erro ao buscar análise de screenshot mais recente: {e}")
            return None
    
    async def get_all_screenshot_analyses(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Recupera todas as análises de screenshot"""
        try:
            result = self.client.table('screenshot_analysis')\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Erro ao buscar análises de screenshot: {e}")
            return []
    
    def generate_sql_file(self, output_path: str = "database_setup.sql") -> bool:
        """Gera arquivo SQL com todas as tabelas e configurações"""
        try:
            sql_content = """-- =====================================================
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
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(sql_content)
            
            print(f"✅ Arquivo SQL gerado com sucesso: {output_path}")
            print("📋 Para usar:")
            print("   1. Abra o SQL Editor no Supabase")
            print("   2. Cole o conteúdo do arquivo")
            print("   3. Execute o script")
            print("   4. Todas as tabelas e configurações serão criadas")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar arquivo SQL: {e}")
            return False
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Recupera estatísticas do banco de dados"""
        try:
            stats = {}
            
            # Estatísticas da tabela match_data
            result = self.client.table('match_data').select('id', count='exact').execute()
            stats['match_data'] = {
                'total_records': result.count if hasattr(result, 'count') else 0
            }
            
            # Estatísticas da tabela filtered_links
            result = self.client.table('filtered_links').select('id', count='exact').execute()
            stats['filtered_links'] = {
                'total_records': result.count if hasattr(result, 'count') else 0
            }
            
            # Estatísticas da tabela match_info
            result = self.client.table('match_info').select('id', count='exact').execute()
            stats['match_info'] = {
                'total_records': result.count if hasattr(result, 'count') else 0
            }
            
            # Estatísticas da tabela screenshot_analysis
            result = self.client.table('screenshot_analysis').select('id', count='exact').execute()
            stats['screenshot_analysis'] = {
                'total_records': result.count if hasattr(result, 'count') else 0
            }
            
            # Partidas ativas
            result = self.client.table('match_info').select('id', count='exact').eq('is_active', True).execute()
            stats['active_matches'] = result.count if hasattr(result, 'count') else 0
            
            return stats
            
        except Exception as e:
            print(f"❌ Erro ao buscar estatísticas: {e}")
            return {}

# Função principal para execução direta do arquivo
async def main():
    """Função principal para execução direta"""
    import sys
    
    print("🚀 DatabaseService - Gerador de SQL")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "generate-sql":
            # Gerar arquivo SQL
            output_file = sys.argv[2] if len(sys.argv) > 2 else "database_setup.sql"
            
            try:
                # Não precisa de conexão para gerar SQL
                service = DatabaseService()
                success = service.generate_sql_file(output_file)
                
                if success:
                    print("\n✅ Arquivo SQL gerado com sucesso!")
                    print(f"📄 Localização: {output_file}")
                else:
                    print("\n❌ Falha ao gerar arquivo SQL")
                    
            except Exception as e:
                print(f"\n❌ Erro: {e}")
                print("💡 Certifique-se de que as variáveis SUPABASE_URL e SUPABASE_ANON_KEY estão configuradas no .env")
        
        elif command == "test-connection":
            # Testar conexão e verificar tabelas
            try:
                service = DatabaseService()
                await service.create_tables_if_not_exist()
                stats = await service.get_database_stats()
                
                print("\n📊 Estatísticas do Banco:")
                for table, data in stats.items():
                    print(f"   {table}: {data}")
                    
            except Exception as e:
                print(f"\n❌ Erro na conexão: {e}")
        
        elif command == "help":
            print_help()
        
        else:
            print(f"❌ Comando desconhecido: {command}")
            print_help()
    
    else:
        print_help()

def print_help():
    """Mostra ajuda de uso"""
    print("\n📋 Comandos disponíveis:")
    print("   python database_service.py generate-sql [arquivo.sql]")
    print("   python database_service.py test-connection")
    print("   python database_service.py help")
    print("\n📝 Exemplos:")
    print("   python database_service.py generate-sql")
    print("   python database_service.py generate-sql meu_banco.sql")
    print("   python database_service.py test-connection")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 