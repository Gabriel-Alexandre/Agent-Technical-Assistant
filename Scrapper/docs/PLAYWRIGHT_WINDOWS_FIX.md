# Correção: Playwright + FastAPI + Windows

## Problema Identificado

O erro `NotImplementedError` ocorria ao tentar usar Playwright dentro de aplicações FastAPI no Windows. Este é um problema conhecido relacionado ao loop de eventos padrão do asyncio no Windows.

### Error Original
```
NotImplementedError
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.2544.0_x64__qbz5n2kfra8p0\Lib\asyncio\subprocess.py", line 223, in create_subprocess_exec
    transport, protocol = await loop.subprocess_exec(
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.2544.0_x64__qbz5n2kfra8p0\Lib\asyncio\base_events.py", line 1708, in subprocess_exec
    transport = await self._make_subprocess_transport(
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.2544.0_x64__qbz5n2kfra8p0\Lib\asyncio\base_events.py", line 503, in _make_subprocess_transport
    raise NotImplementedError
```

## Causa do Problema

No Windows, o asyncio usa por padrão o `SelectorEventLoop`, que não suporta subprocessos. O Playwright precisa criar subprocessos para controlar o navegador, causando a incompatibilidade.

## Solução Implementada

### 1. Configuração do ProactorEventLoop

**Arquivo modificado**: `main.py`

```python
# Configuração do Event Loop para Windows (deve estar antes de outros imports)
import sys
import asyncio
import platform

# Configurar ProactorEventLoop no Windows para compatibilidade com Playwright
if platform.system() == "Windows":
    # Definir política de event loop para Windows
    if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    else:
        # Para versões mais antigas do Python no Windows
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
```

### 2. Servidor Customizado para Desenvolvimento

**Arquivo modificado**: `main.py` (seção `if __name__ == "__main__"`):

```python
if platform.system() == "Windows":
    print("🪟 Sistema Windows detectado - usando ProactorEventLoop para compatibilidade com Playwright")
    
    # Para desenvolvimento com reload no Windows
    class ProactorServer(uvicorn.Server):
        def run(self, sockets=None):
            # Garantir que o ProactorEventLoop está configurado
            if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
            asyncio.run(self.serve(sockets=sockets))
    
    config = uvicorn.Config(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    server = ProactorServer(config=config)
    server.run()
```

### 3. Logs de Debug

**Arquivo modificado**: `services.py`

Adicionamos logs para verificar qual loop está sendo usado:

```python
# Verificar e exibir informações do event loop
import platform
loop = asyncio.get_running_loop()
print(f"🔧 Sistema: {platform.system()}")
print(f"🔧 Event Loop: {type(loop).__name__}")
print(f"🔧 Event Loop Policy: {type(asyncio.get_event_loop_policy()).__name__}")
```

## Como Testar a Correção

### 1. Teste Independente

Execute o script de teste:

```bash
cd Scrapper
python test_playwright_windows.py
```

### 2. Teste com a API

Inicie a API:

```bash
cd Scrapper
python main.py
```

Faça uma requisição:

```bash
curl -X POST "http://localhost:8000/match/13616168/full-data"
```

## Resultados Esperados

### ✅ Logs de Sucesso:
```
🪟 Sistema Windows detectado - usando ProactorEventLoop para compatibilidade com Playwright
🔧 Sistema: Windows
🔧 Event Loop: ProactorEventLoop
🔧 Event Loop Policy: WindowsProactorEventLoopPolicy
✅ Playwright context criado
✅ Browser Chromium iniciado
```

### ❌ Logs de Problema (antes da correção):
```
🔧 Sistema: Windows
🔧 Event Loop: SelectorEventLoop
🔧 Event Loop Policy: WindowsSelectorEventLoopPolicy
NotImplementedError
```

## Considerações Importantes

### Performance
- O `ProactorEventLoop` pode ser ligeiramente mais lento que o `SelectorEventLoop`
- A diferença é mínima e compensa pela compatibilidade com Playwright

### Compatibilidade
- A solução é específica para Windows
- No Linux/Mac, continua usando a configuração padrão
- Totalmente compatível com FastAPI e Uvicorn

### Reload
- O reload durante desenvolvimento funciona normalmente
- A configuração do loop é replicada a cada restart

## Fontes da Solução

Esta solução foi baseada em:

1. [FastAPI GitHub Discussion #6485](https://github.com/fastapi/fastapi/discussions/6485)
2. [FastAPI GitHub Issue #5446](https://github.com/tiangolo/fastapi/issues/5446)
3. [Documentação oficial do Python sobre asyncio no Windows](https://docs.python.org/3/library/asyncio-platforms.html#windows)

## Resumo

A configuração do `WindowsProactorEventLoopPolicy` resolve completamente o erro `NotImplementedError` ao usar Playwright com FastAPI no Windows, mantendo total compatibilidade e funcionalidade da aplicação. 