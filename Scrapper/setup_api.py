"""
Script de Configuração da API SofaScore
Automatiza a configuração inicial da API
"""

import os
import sys
import asyncio
from pathlib import Path
from database_service import DatabaseService

def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    print("🔍 Verificando ambiente...")
    
    # Verificar se está na pasta correta
    if not Path("main.py").exists():
        print("❌ Execute este script na pasta /Scrapper")
        return False
    
    # Verificar arquivo .env
    if not Path(".env").exists():
        print("⚠️ Arquivo .env não encontrado")
        print("📝 Crie um arquivo .env com as seguintes variáveis:")
        print("SUPABASE_URL=sua_url_supabase")
        print("SUPABASE_ANON_KEY=sua_chave_anonima")
        print("OPENAI_API_KEY=sua_chave_openai")
        return False
    
    print("✅ Ambiente verificado")
    return True

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("📦 Verificando dependências...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'supabase', 
        'openai', 'playwright', 
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Dependências faltando: {', '.join(missing_packages)}")
        print("📝 Execute: pip install -r requirements.txt")
        return False
    
    print("✅ Dependências verificadas")
    return True

async def setup_database():
    """Configura o banco de dados"""
    print("🗄️ Configurando banco de dados...")
    
    try:
        db_service = DatabaseService()
        await db_service.create_tables_if_not_exist()
        print("✅ Banco de dados configurado")
        return True
    except Exception as e:
        print(f"❌ Erro na configuração do banco: {e}")
        return False

def install_playwright():
    """Instala navegadores do Playwright"""
    print("🌐 Instalando navegadores Playwright...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Playwright configurado")
            return True
        else:
            print(f"❌ Erro no Playwright: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro na instalação do Playwright: {e}")
        return False

def create_database_sql():
    """Cria arquivo SQL para o Supabase"""
    sql_content = """
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
"""
    
    with open("supabase_setup.sql", "w", encoding="utf-8") as f:
        f.write(sql_content)
    
    print("📄 Arquivo supabase_setup.sql criado")
    print("💡 Execute este SQL no Supabase SQL Editor")

async def main():
    """Função principal de configuração"""
    print("🚀 Configurando API SofaScore Data Collector...")
    print("=" * 50)
    
    # Verificar ambiente
    if not check_environment():
        return
    
    # Verificar dependências
    if not check_dependencies():
        return
    
    # Instalar Playwright
    if not install_playwright():
        print("⚠️ Continuando sem Playwright (pode afetar coleta de dados)")
    
    # Criar arquivo SQL
    create_database_sql()
    
    # Configurar banco de dados
    if not await setup_database():
        print("⚠️ Configuração do banco pode ser necessária via SQL Editor")
    
    print("\n" + "="*50)
    print("✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("\n📋 Próximos passos:")
    print("1. Verifique se o arquivo .env está configurado corretamente")
    print("2. Execute o SQL supabase_setup.sql no Supabase (se necessário)")
    print("3. Execute: python main.py")
    print("4. Acesse: http://localhost:8000/docs")
    print("\n🎯 Endpoints disponíveis:")
    print("• POST /match/{match_id}/full-data")
    print("• POST /match/{match_id}/simplified-data")
    print("• POST /match/{match_id}/analysis")
    print("• GET /match/{match_id}/history")

if __name__ == "__main__":
    asyncio.run(main()) 