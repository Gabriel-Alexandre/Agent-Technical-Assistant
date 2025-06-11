#!/bin/bash

echo "🚀 Iniciando container SofaScore Scrapper..."
echo "📅 $(date)"

# Verificar se o Playwright está instalado
echo "🔍 Verificando instalação do Playwright..."
python -c "import playwright; print('✅ Playwright Python library OK')" || {
    echo "❌ Playwright não está instalado!"
    exit 1
}

# Verificar se os navegadores estão instalados
echo "🔍 Verificando navegadores do Playwright..."
python -c "
import os
from playwright.sync_api import sync_playwright

try:
    with sync_playwright() as p:
        chromium_path = p.chromium.executable_path
        print(f'🔍 Caminho do Chromium: {chromium_path}')
        
        if os.path.exists(chromium_path):
            print('✅ Chromium encontrado e verificado!')
        else:
            print('❌ Chromium não encontrado!')
            exit(1)
except Exception as e:
    print(f'❌ Erro ao verificar Chromium: {e}')
    exit(1)
" || {
    echo "🔄 Instalando navegadores do Playwright..."
    playwright install chromium || {
        echo "❌ Falha ao instalar Chromium!"
        exit 1
    }
    
    echo "🔄 Instalando dependências do sistema..."
    playwright install-deps chromium || {
        echo "⚠️ Aviso: Algumas dependências podem não ter sido instaladas"
    }
    
    echo "✅ Instalação concluída!"
}

# Verificar permissões dos diretórios
echo "🔍 Verificando permissões dos diretórios..."
for dir in data live_data live_data_simplify analysis logs; do
    if [ ! -d "/app/$dir" ]; then
        echo "📁 Criando diretório: $dir"
        mkdir -p "/app/$dir"
    fi
    
    # Ajustar permissões se necessário
    if [ ! -w "/app/$dir" ]; then
        echo "🔧 Ajustando permissões para $dir"
        # Como não somos root aqui, vamos apenas verificar se podemos criar arquivos
        touch "/app/$dir/.test" 2>/dev/null && {
            rm "/app/$dir/.test"
            echo "✅ Permissões OK para $dir"
        } || {
            echo "⚠️ Aviso: Sem permissão de escrita em $dir"
        }
    else
        echo "✅ Permissões OK para $dir"
    fi
done

# Verificar conectividade básica
echo "🌐 Testando conectividade..."
curl -s --connect-timeout 5 https://www.google.com > /dev/null && {
    echo "✅ Conectividade básica OK"
} || {
    echo "⚠️ Aviso: Problemas de conectividade detectados"
}

# Verificar recursos do sistema
echo "💻 Recursos do sistema:"
echo "   🧠 Memória disponível: $(free -h | awk '/^Mem:/ {print $7}')"
echo "   💾 Espaço em disco: $(df -h /app | awk 'NR==2 {print $4}')"
echo "   🔧 CPUs disponíveis: $(nproc)"

# Testar importação crítica antes de iniciar
echo "🧪 Testando importações críticas..."
python -c "
import asyncio
import platform
from playwright.async_api import async_playwright

print(f'🔧 Sistema: {platform.system()}')
print(f'🔧 Python: {platform.python_version()}')
print(f'🔧 Event Loop: {type(asyncio.new_event_loop()).__name__}')
print('✅ Todas as importações OK!')
" || {
    echo "❌ Falha nas importações críticas!"
    exit 1
}

echo "🎯 Tudo pronto! Iniciando aplicação..."
echo "=" * 50

# Executar o comando original
exec "$@" 