"""
Script de teste para verificar compatibilidade do Playwright com Windows
Testa se a configuração do ProactorEventLoop resolve o erro NotImplementedError
"""

import sys
import asyncio
import platform

# Configurar ProactorEventLoop no Windows
if platform.system() == "Windows":
    print("🪟 Windows detectado - configurando ProactorEventLoop")
    if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    else:
        # Para versões mais antigas do Python no Windows
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)

async def test_playwright():
    """Teste básico do Playwright"""
    try:
        from playwright.async_api import async_playwright
        print("✅ Playwright importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Playwright: {e}")
        return False
    
    # Informações do event loop
    loop = asyncio.get_running_loop()
    print(f"🔧 Sistema: {platform.system()}")
    print(f"🔧 Event Loop: {type(loop).__name__}")
    print(f"🔧 Event Loop Policy: {type(asyncio.get_event_loop_policy()).__name__}")
    
    try:
        print("🚀 Iniciando teste do Playwright...")
        
        async with async_playwright() as p:
            print("✅ Playwright context criado")
            
            # Configuração mínima do browser
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--single-process'
                ]
            )
            print("✅ Browser Chromium iniciado")
            
            # Criar contexto e página
            context = await browser.new_context()
            page = await context.new_page()
            print("✅ Página criada")
            
            # Teste simples de navegação
            await page.goto("https://httpbin.org/get", timeout=10000)
            print("✅ Navegação bem-sucedida")
            
            # Verificar conteúdo
            title = await page.title()
            print(f"✅ Título da página: {title}")
            
            # Cleanup
            await browser.close()
            print("✅ Browser fechado")
            
        print("🎉 Teste do Playwright concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste do Playwright: {e}")
        print(f"❌ Tipo do erro: {type(e).__name__}")
        return False

async def main():
    """Função principal de teste"""
    print("=" * 50)
    print("🧪 TESTE DE COMPATIBILIDADE PLAYWRIGHT + WINDOWS")
    print("=" * 50)
    
    success = await test_playwright()
    
    print("=" * 50)
    if success:
        print("✅ TESTE PASSOU - Playwright funcionando corretamente!")
        print("✅ A configuração do ProactorEventLoop resolveu o problema")
    else:
        print("❌ TESTE FALHOU - Ainda há problemas com o Playwright")
        print("❌ Verifique se o Playwright está instalado: playwright install chromium")
    print("=" * 50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro crítico no teste: {e}") 