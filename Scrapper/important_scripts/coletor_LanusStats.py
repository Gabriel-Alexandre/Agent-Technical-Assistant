"""
Coletor para obter partidas ao vivo usando SofaScore
"""

import asyncio
import json
import requests
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path

class ColetorPartidasAoVivo:
    """Coletor para obter partidas ao vivo do SofaScore"""
    
    def __init__(self):
        self.sofascore_base_url = "https://api.sofascore.com/api/v1/"
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
    async def obter_partidas_ao_vivo_sofascore(self):
        """Obtém partidas ao vivo do SofaScore usando Playwright"""
        partidas_ao_vivo = []
        
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                extra_http_headers={
                    'Accept': 'application/json',
                    'Accept-Language': 'pt-BR,pt;q=0.9',
                    'Referer': 'https://www.sofascore.com/'
                }
            )
            
            page = await context.new_page()
            
            try:
                # URL para partidas ao vivo do SofaScore
                url = f"{self.sofascore_base_url}sport/football/events/live"
                
                response = await page.goto(url, wait_until='networkidle', timeout=30000)
                
                if response.status == 200:
                    content = await page.content()
                    
                    # Extrair JSON do conteúdo
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    
                    if json_start != -1 and json_end > json_start:
                        json_content = content[json_start:json_end]
                        data = json.loads(json_content)
                        
                        if 'events' in data:
                            # Salvar todos os dados completos da API
                            partidas_ao_vivo = data['events']
                    
            except Exception as e:
                print(f"❌ Erro ao obter partidas do SofaScore: {e}")
                
            finally:
                await browser.close()
        
        return partidas_ao_vivo
    
    async def listar_todas_partidas_ao_vivo(self):
        """Lista todas as partidas ao vivo do SofaScore e salva em JSON"""
        
        # Obter partidas do SofaScore
        partidas_sofascore = await self.obter_partidas_ao_vivo_sofascore()
        
        # Preparar dados para salvar (mantendo estrutura completa da API)
        dados_para_salvar = {
            'timestamp': datetime.now().isoformat(),
            'total_partidas': len(partidas_sofascore),
            'fonte': 'SofaScore',
            'api_endpoint': 'sport/football/events/live',
            'events': partidas_sofascore
        }
        
        # Salvar JSON na pasta results
        timestamp_arquivo = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"partidas_ao_vivo_{timestamp_arquivo}.json"
        caminho_arquivo = self.results_dir / nome_arquivo
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_para_salvar, f, indent=2, ensure_ascii=False)
        
        return partidas_sofascore

    async def obter_dados_completos_partida(self, partida_id):
        """Obtém todos os dados relevantes de uma partida específica usando o ID"""
        print(f"🔍 Obtendo dados completos da partida ID: {partida_id}")
        
        dados_partida = {
            'partida_id': partida_id,
            'timestamp_coleta': datetime.now().isoformat(),
            'dados_coletados': {}
        }
        
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                extra_http_headers={
                    'Accept': 'application/json',
                    'Accept-Language': 'pt-BR,pt;q=0.9',
                    'Referer': 'https://www.sofascore.com/'
                }
            )
            
            # Endpoints que realmente existem e são relevantes para a partida
            endpoints_relevantes = {
                'dados_gerais': f"event/{partida_id}",
                'estatisticas': f"event/{partida_id}/statistics",
                'incidentes': f"event/{partida_id}/incidents",
                'escalacoes': f"event/{partida_id}/lineups",
                'shotmap': f"event/{partida_id}/shotmap",
                'momentum': f"event/{partida_id}/graph",
                'posicoes_medias': f"event/{partida_id}/average-positions"
            }
            
            async def coletar_endpoint(nome, endpoint):
                """Função para coletar dados de um endpoint específico"""
                try:
                    page = await context.new_page()
                    url = f"{self.sofascore_base_url}{endpoint}"
                    
                    response = await page.goto(url, wait_until='networkidle', timeout=10000)
                    
                    if response.status == 200:
                        content = await page.content()
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        
                        if json_start != -1 and json_end > json_start:
                            json_content = content[json_start:json_end]
                            data = json.loads(json_content)
                            print(f"    ✅ {nome} coletado com sucesso")
                            await page.close()
                            return nome, data
                        else:
                            print(f"    ⚠️ {nome}: Não foi possível extrair JSON")
                            await page.close()
                            return nome, None
                    else:
                        print(f"    ❌ {nome}: Status {response.status}")
                        await page.close()
                        return nome, None
                        
                except Exception as e:
                    print(f"    ❌ Erro ao coletar {nome}: {e}")
                    try:
                        await page.close()
                    except:
                        pass
                    return nome, None
            
            # Coletar dados principais em paralelo
            print(f"🏈 Coletando dados principais da partida em paralelo...")
            tasks = [coletar_endpoint(nome, endpoint) for nome, endpoint in endpoints_relevantes.items()]
            resultados = await asyncio.gather(*tasks)
            
            # Processar resultados
            for nome, data in resultados:
                dados_partida['dados_coletados'][nome] = data
            
            # Coletar dados dos jogadores se temos as escalações
            escalacoes_data = dados_partida['dados_coletados'].get('escalacoes')
            if escalacoes_data:
                print(f"🔥 Coletando dados individuais dos jogadores em paralelo...")
                
                async def coletar_dados_jogador(team, player_data):
                    """Coleta dados de um jogador específico"""
                    if 'player' not in player_data or 'id' not in player_data['player']:
                        return None
                    
                    player_id = player_data['player']['id']
                    player_name = player_data['player'].get('name', f'Player_{player_id}')
                    
                    player_info = {
                        'basic_info': player_data,
                        'heatmap': None,
                        'statistics': None
                    }
                    
                    try:
                        page = await context.new_page()
                        
                        # Coletar heatmap
                        try:
                            heatmap_url = f"{self.sofascore_base_url}event/{partida_id}/player/{player_id}/heatmap"
                            response = await page.goto(heatmap_url, wait_until='networkidle', timeout=8000)
                            
                            if response.status == 200:
                                content = await page.content()
                                json_start = content.find('{')
                                json_end = content.rfind('}') + 1
                                
                                if json_start != -1 and json_end > json_start:
                                    json_content = content[json_start:json_end]
                                    heatmap_data = json.loads(json_content)
                                    player_info['heatmap'] = heatmap_data
                        except:
                            pass
                        
                        # Coletar estatísticas do jogador na partida
                        try:
                            # Usar as estatísticas que já vêm nas escalações
                            if 'statistics' in player_data:
                                player_info['statistics'] = player_data['statistics']
                        except:
                            pass
                        
                        await page.close()
                        print(f"    ✅ Dados de {player_name} coletados")
                        return team, player_name, player_info
                        
                    except Exception as e:
                        print(f"    ⚠️ Erro nos dados de {player_name}: {e}")
                        try:
                            await page.close()
                        except:
                            pass
                        return team, player_name, None
                
                # Preparar tasks para todos os jogadores
                player_tasks = []
                for team in ['home', 'away']:
                    if team in escalacoes_data and 'players' in escalacoes_data[team]:
                        for player_data in escalacoes_data[team]['players']:
                            player_tasks.append(coletar_dados_jogador(team, player_data))
                
                # Executar coleta de jogadores em paralelo (em lotes para não sobrecarregar)
                dados_jogadores = {'home': {}, 'away': {}}
                
                # Processar em lotes de 10 jogadores por vez
                batch_size = 10
                for i in range(0, len(player_tasks), batch_size):
                    batch = player_tasks[i:i + batch_size]
                    batch_results = await asyncio.gather(*batch)
                    
                    for result in batch_results:
                        if result and len(result) == 3:
                            team, player_name, player_info = result
                            if player_info:
                                dados_jogadores[team][player_name] = player_info
                
                dados_partida['dados_coletados']['jogadores_detalhados'] = dados_jogadores
            
            await browser.close()
        
        # Adicionar informações de resumo
        dados_coletados_com_sucesso = sum(1 for v in dados_partida['dados_coletados'].values() if v is not None)
        total_endpoints = len(endpoints_relevantes) + (1 if escalacoes_data else 0)  # +1 para jogadores se disponível
        
        dados_partida['resumo_coleta'] = {
            'total_endpoints': total_endpoints,
            'coletados_com_sucesso': dados_coletados_com_sucesso,
            'taxa_sucesso': f"{(dados_coletados_com_sucesso/total_endpoints)*100:.1f}%",
            'endpoints_falharam': [nome for nome, dados in dados_partida['dados_coletados'].items() if dados is None],
            'dados_relevantes_coletados': {
                'dados_basicos': ['dados_gerais', 'estatisticas', 'incidentes', 'escalacoes'],
                'dados_avancados': ['shotmap', 'momentum', 'posicoes_medias'],
                'dados_contextuais': [],
                'dados_jogadores': ['jogadores_detalhados'] if escalacoes_data else []
            },
            'estatisticas_disponiveis': [
                'Dados gerais da partida (times, placar, status)',
                'Estatísticas completas (posse, chutes, passes, etc.)',
                'Timeline de eventos (gols, cartões, substituições)',
                'Escalações e formações táticas',
                'Mapa de chutes (shotmap)',
                'Gráfico de momentum',
                'Posições médias dos jogadores',
                'Heatmaps individuais dos jogadores',
                'Estatísticas individuais dos jogadores'
            ]
        }
        
        # Salvar dados em arquivo JSON separado
        timestamp_arquivo = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"partida_completa_{partida_id}_{timestamp_arquivo}.json"
        caminho_arquivo = self.results_dir / nome_arquivo
        
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_partida, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Dados da partida salvos em: {caminho_arquivo.absolute()}")
            print(f"📊 Resumo: {dados_coletados_com_sucesso}/{total_endpoints} endpoints coletados com sucesso")
            
            # Mostrar estatísticas por categoria
            for categoria, itens in dados_partida['resumo_coleta']['dados_relevantes_coletados'].items():
                if itens:  # Só mostrar se há itens na categoria
                    coletados = sum(1 for item in itens if dados_partida['dados_coletados'].get(item) is not None)
                    print(f"   {categoria}: {coletados}/{len(itens)} itens")
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
        
        return dados_partida

async def main():
    """Função principal com menu de opções"""
    print("🏆 COLETOR DE PARTIDAS DE FUTEBOL - SofaScore")
    print("=" * 60)
    print("Escolha uma opção:")
    print("1 - Listar TODAS as partidas ao vivo")
    print("2 - Obter dados completos de uma partida específica")
    print("=" * 60)
    
    try:
        opcao = input("Digite sua opção (1 ou 2): ").strip()
        
        coletor = ColetorPartidasAoVivo()
        
        if opcao == "1":
            print("🚀 Iniciando busca por partidas ao vivo...")
            partidas = await coletor.listar_todas_partidas_ao_vivo()
            
            print(f"✅ {len(partidas)} partidas ao vivo encontradas e salvas")
            print("=" * 60)
            print("🏁 Busca concluída!")
            
            return partidas
            
        elif opcao == "2":
            partida_id = input("Digite o ID da partida: ").strip()
            
            if not partida_id:
                print("❌ ID da partida não pode estar vazio!")
                return None
            
            print(f"🚀 Iniciando coleta de dados da partida {partida_id}...")
            dados_partida = await coletor.obter_dados_completos_partida(partida_id)
            
            print("=" * 60)
            print("🏁 Coleta de dados concluída!")
            
            return dados_partida
            
        else:
            print("❌ Opção inválida! Use 1 ou 2.")
            return await main()
            
    except KeyboardInterrupt:
        print("\n⏹️ Execução interrompida pelo usuário.")
        return None
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(main())
