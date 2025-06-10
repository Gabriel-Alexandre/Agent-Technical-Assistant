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
        print("✅ Cliente Supabase inicializado com sucesso!")
    
    async def create_tables_if_not_exist(self):
        """Cria tabelas necessárias se não existirem"""
        try:
            # SQL para criar tabelas
            create_tables_sql = """
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
            """
            
            # Executar SQL através de uma function edge (se disponível) ou RPC
            # Como fallback, vamos tentar criar as tabelas via RPC
            print("🔄 Criando tabelas no Supabase...")
            
            # Para Supabase, vamos usar uma abordagem mais simples
            # Verificar se a tabela existe consultando
            try:
                result = self.client.table('match_data').select('id').limit(1).execute()
                print("✅ Tabela match_data já existe")
            except Exception:
                print("📝 Tabela match_data não existe, criação necessária via SQL Editor do Supabase")
                print("📋 Execute o seguinte SQL no SQL Editor do Supabase:")
                print("="*60)
                print(create_tables_sql)
                print("="*60)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar/criar tabelas: {e}")
            print("📝 Execute manualmente o SQL no Supabase:")
            print(create_tables_sql)
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
                print(f"✅ Dados salvos no Supabase - ID: {record_id}")
                return record_id
            else:
                print(f"❌ Erro ao salvar no Supabase: {result}")
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