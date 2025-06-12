"""
Capturador de prints de partidas do SofaScore
Tira screenshots da página completa de uma partida específica
"""

import asyncio
import sys
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path
import json
import re

class SofaScoreScreenshotCollector:
    """Coletor de prints de partidas do SofaScore"""
    
    def __init__(self):
        self.website_url = "https://www.sofascore.com/"
        self.prints_dir = Path("prints-matchs")
        self.prints_dir.mkdir(exist_ok=True)
        self.links_dir = Path("links")
        self.links_dir.mkdir(exist_ok=True)
        
    async def create_browser_context(self, playwright):
        """Cria contexto do navegador com configurações realistas"""
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='pt-BR',
            timezone_id='America/Sao_Paulo',
            extra_http_headers={
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        return browser, context
    
    async def get_all_links_from_homepage(self):
        """Acessa a página inicial do SofaScore e coleta todos os links"""
        async with async_playwright() as playwright:
            browser, context = await self.create_browser_context(playwright)
            page = await context.new_page()
            
            try:
                # Acessar página inicial em português
                homepage_url = "https://www.sofascore.com/pt/"
                response = await page.goto(homepage_url, timeout=15000)
                
                if response.status != 200:
                    print(f"❌ Erro ao acessar página inicial: Status {response.status}")
                    return None
                
                # Aguardar carregamento completo
                await asyncio.sleep(3)
                
                # Aceitar cookies se aparecer o banner
                try:
                    cookie_button = page.locator('button:has-text("Accept"), button:has-text("Aceitar"), button:has-text("Concordo"), [data-testid="cookie-accept"]')
                    if await cookie_button.count() > 0:
                        await cookie_button.first.click()
                        await asyncio.sleep(2)
                except:
                    pass  # Ignorar se não houver banner de cookies
                
                # Coletar todos os elementos <a> com href
                links_elements = await page.locator('a[href]').all()
                
                links_data = {
                    "collected_at": datetime.now().isoformat(),
                    "homepage_url": homepage_url,
                    "total_links": 0,
                    "links": [],
                    "categories": {
                        "matches": [],
                        "teams": [],
                        "tournaments": [],
                        "players": [],
                        "other": []
                    }
                }
                
                for link_element in links_elements:
                    try:
                        href = await link_element.get_attribute('href')
                        text = await link_element.text_content()
                        title = await link_element.get_attribute('title')
                        
                        if href:
                            # Converter links relativos em absolutos
                            if href.startswith('/'):
                                full_url = f"https://www.sofascore.com{href}"
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue  # Pular links inválidos
                            
                            # Limpar texto
                            text = text.strip() if text else ""
                            title = title.strip() if title else ""
                            
                            link_info = {
                                "url": full_url,
                                "text": text,
                                "title": title,
                                "href_original": href
                            }
                            
                            links_data["links"].append(link_info)
                            
                            # Categorizar links
                            if '/match/' in href or '/game/' in href:
                                links_data["categories"]["matches"].append(link_info)
                            elif '/team/' in href or '/club/' in href:
                                links_data["categories"]["teams"].append(link_info)
                            elif '/tournament/' in href or '/league/' in href or '/competition/' in href:
                                links_data["categories"]["tournaments"].append(link_info)
                            elif '/player/' in href:
                                links_data["categories"]["players"].append(link_info)
                            else:
                                links_data["categories"]["other"].append(link_info)
                                
                    except Exception as e:
                        continue
                
                links_data["total_links"] = len(links_data["links"])
                
                # Salvar dados dos links
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"all-links_{timestamp}.json"
                filepath = self.links_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(links_data, f, indent=2, ensure_ascii=False)
                
                # Mostrar estatísticas
                print("=" * 60)
                print("📊 ESTATÍSTICAS DOS LINKS COLETADOS")
                print("=" * 60)
                print(f"🔗 Total de links: {links_data['total_links']}")
                print(f"⚽ Partidas: {len(links_data['categories']['matches'])}")
                print(f"🏆 Times: {len(links_data['categories']['teams'])}")
                print(f"🏅 Torneios: {len(links_data['categories']['tournaments'])}")
                print(f"👤 Jogadores: {len(links_data['categories']['players'])}")
                print(f"📄 Outros: {len(links_data['categories']['other'])}")
                print("=" * 60)
                
                # Mostrar alguns exemplos de cada categoria
                categories_display = {
                    "matches": "⚽ PARTIDAS",
                    "teams": "🏆 TIMES", 
                    "tournaments": "🏅 TORNEIOS",
                    "players": "👤 JOGADORES"
                }
                
                for category, title in categories_display.items():
                    category_links = links_data["categories"][category]
                    if category_links:
                        print(f"\n{title} (primeiros 5):")
                        for i, link in enumerate(category_links[:5]):
                            text_display = link["text"][:50] + "..." if len(link["text"]) > 50 else link["text"]
                            if text_display:
                                print(f"  {i+1}. {text_display}")
                                print(f"     {link['url']}")
                            else:
                                print(f"  {i+1}. [Sem texto]")
                                print(f"     {link['url']}")
                
                return links_data
                
            except Exception as e:
                print(f"❌ Erro ao coletar links: {e}")
                return None
                
            finally:
                await browser.close()
    
    def process_links_json(self, json_file_path):
        """Processa o JSON de links e extrai apenas links com formato específico"""
        try:
            print(f"🔄 Processando arquivo: {json_file_path}")
            
            # Carregar dados do JSON
            with open(json_file_path, 'r', encoding='utf-8') as f:
                links_data = json.load(f)
            
            print(f"📊 Total de links no arquivo: {links_data.get('total_links', 0)}")
            
            # Padrão regex para o formato: 7 letras + #id: + 8 números
            # Exemplo: fxcspxc#id:13970328
            pattern = r'[a-zA-Z]{7}#id:\d{8}$'
            
            filtered_links = []
            
            # Processar todos os links
            all_links = links_data.get('links', [])
            
            for link in all_links:
                url = link.get('url', '')
                
                # Verificar se a URL termina com o padrão desejado
                if re.search(pattern, url):
                    filtered_links.append({
                        'url': url,
                        'text': link.get('text', ''),
                        'title': link.get('title', ''),
                        'match_id': self.extract_match_id_from_url(url)
                    })
            
            print(f"✅ Links encontrados com o padrão: {len(filtered_links)}")
            
            if filtered_links:
                # Criar dados processados
                processed_data = {
                    "processed_at": datetime.now().isoformat(),
                    "source_file": str(json_file_path),
                    "pattern_used": pattern,
                    "total_filtered_links": len(filtered_links),
                    "filtered_links": filtered_links
                }
                
                # Salvar dados processados
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                processed_filename = f"filtered-links_{timestamp}.json"
                processed_filepath = self.links_dir / processed_filename
                
                with open(processed_filepath, 'w', encoding='utf-8') as f:
                    json.dump(processed_data, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Links filtrados salvos em: {processed_filepath.absolute()}")
                
                # Mostrar alguns exemplos
                print("\n" + "=" * 60)
                print("🔗 EXEMPLOS DE LINKS FILTRADOS")
                print("=" * 60)
                
                for i, link in enumerate(filtered_links[:10]):  # Mostrar até 10 exemplos
                    print(f"{i+1}. {link['text'][:50]}..." if len(link['text']) > 50 else f"{i+1}. {link['text']}")
                    print(f"   URL: {link['url']}")
                    print(f"   Match ID: {link['match_id']}")
                    print()
                
                if len(filtered_links) > 10:
                    print(f"... e mais {len(filtered_links) - 10} links")
                
                print("=" * 60)
                
                return processed_data
            else:
                print("⚠️ Nenhum link encontrado com o padrão especificado")
                return None
                
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {json_file_path}")
            return None
        except json.JSONDecodeError:
            print(f"❌ Erro ao decodificar JSON: {json_file_path}")
            return None
        except Exception as e:
            print(f"❌ Erro ao processar arquivo: {e}")
            return None
    
    def extract_match_id_from_url(self, url):
        """Extrai o ID da partida da URL"""
        try:
            # Procurar pelo padrão #id:XXXXXXXX
            match = re.search(r'#id:(\d{8})', url)
            if match:
                return match.group(1)
            return None
        except:
            return None
    
    def extract_match_id_from_identifier(self, match_identifier):
        """Extrai o match_id de um identificador (URL completa, slug ou ID)"""
        try:
            # Se já é apenas um ID numérico
            if match_identifier.isdigit() and len(match_identifier) == 8:
                return match_identifier
            
            # Se contém #id:, extrair o ID
            match = re.search(r'#id:(\d{8})', match_identifier)
            if match:
                return match.group(1)
            
            # Se não encontrou, retornar o identificador original
            return match_identifier
        except:
            return match_identifier
    
    def build_match_url(self, match_identifier):
        """Constrói a URL completa da partida baseada no identificador"""
        try:
            # Se já é uma URL completa
            if match_identifier.startswith('http'):
                return match_identifier
            
            # Se é apenas um ID numérico (formato antigo)
            if match_identifier.isdigit() and len(match_identifier) == 8:
                return f"https://www.sofascore.com/match/{match_identifier}"
            
            # Se é um slug com formato: nome-times/codigo#id:12345678
            if '/' in match_identifier and '#id:' in match_identifier:
                return f"https://www.sofascore.com/pt/football/match/{match_identifier}"
            
            # Se é apenas o slug sem #id:
            if '/' in match_identifier:
                return f"https://www.sofascore.com/pt/football/match/{match_identifier}"
            
            # Fallback: assumir que é um ID
            return f"https://www.sofascore.com/match/{match_identifier}"
            
        except Exception as e:
            print(f"⚠️ Erro ao construir URL: {e}")
            return f"https://www.sofascore.com/match/{match_identifier}"
    
    def find_latest_links_file(self):
        """Encontra o arquivo de links mais recente"""
        try:
            links_files = list(self.links_dir.glob("all-links_*.json"))
            if not links_files:
                print("❌ Nenhum arquivo de links encontrado na pasta links/")
                return None
            
            # Ordenar por data de modificação (mais recente primeiro)
            latest_file = max(links_files, key=lambda f: f.stat().st_mtime)
            print(f"📄 Arquivo mais recente encontrado: {latest_file.name}")
            return latest_file
            
        except Exception as e:
            print(f"❌ Erro ao buscar arquivos: {e}")
            return None
    
    async def take_match_screenshot(self, match_identifier):
        """Tira screenshot da página completa de uma partida"""
        async with async_playwright() as playwright:
            browser, context = await self.create_browser_context(playwright)
            page = await context.new_page()
            
            try:
                print(f"🔄 Acessando página da partida {match_identifier}...")
                
                # Construir URL da partida
                match_url = self.build_match_url(match_identifier)
                
                # Navegar para a página
                response = await page.goto(match_url, timeout=30000)
                
                if response.status != 200:
                    print(f"❌ Erro ao acessar página: Status {response.status}")
                    return None
                
                # Aguardar um pouco para garantir que tudo carregou
                await asyncio.sleep(3)
                
                # Aceitar cookies se aparecer o banner
                try:
                    cookie_button = page.locator('button:has-text("Accept"), button:has-text("Aceitar"), [data-testid="cookie-accept"]')
                    if await cookie_button.count() > 0:
                        await cookie_button.first.click()
                        await asyncio.sleep(1)
                except:
                    pass  # Ignorar se não houver banner de cookies
                
                # Obter informações da partida para o nome do arquivo
                try:
                    # Tentar obter nomes dos times
                    home_team_element = page.locator('[data-testid="match_header_team_home"] .team-name, .home-team .team-name')
                    away_team_element = page.locator('[data-testid="match_header_team_away"] .team-name, .away-team .team-name')
                    
                    home_team = "Home"
                    away_team = "Away"
                    
                    if await home_team_element.count() > 0:
                        home_team = await home_team_element.first.text_content()
                        home_team = home_team.strip() if home_team else "Home"
                    
                    if await away_team_element.count() > 0:
                        away_team = await away_team_element.first.text_content()
                        away_team = away_team.strip() if away_team else "Away"
                    
                    # Limpar nomes dos times para usar no nome do arquivo
                    home_team = "".join(c for c in home_team if c.isalnum() or c in (' ', '-', '_')).strip()
                    away_team = "".join(c for c in away_team if c.isalnum() or c in (' ', '-', '_')).strip()
                    
                except Exception as e:
                    home_team = "Home"
                    away_team = "Away"
                
                # Extrair match_id para o nome do arquivo
                match_id = self.extract_match_id_from_identifier(match_identifier)
                
                # Criar nome do arquivo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"match_{match_id}_{home_team}_vs_{away_team}_{timestamp}.png"
                # Remover caracteres especiais do nome do arquivo
                filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).strip()
                filepath = self.prints_dir / filename
                
                # Tirar screenshot da página inteira
                await page.screenshot(
                    path=str(filepath),
                    full_page=True,
                    type='png'
                )
                
                return filepath
                
            except Exception as e:
                print(f"❌ Erro ao tirar screenshot: {e}")
                return None
                
            finally:
                await browser.close()
    
    async def take_multiple_screenshots(self, match_identifier, sections=None):
        """Tira screenshots de seções específicas da partida"""
        if sections is None:
            sections = ['overview', 'statistics', 'lineups', 'timeline']
        
        async with async_playwright() as playwright:
            browser, context = await self.create_browser_context(playwright)
            page = await context.new_page()
            
            try:
                match_url = self.build_match_url(match_identifier)
                response = await page.goto(match_url, timeout=30000)
                
                if response.status != 200:
                    print(f"❌ Erro ao acessar página: Status {response.status}")
                    return []
                
                await asyncio.sleep(3)
                
                # Aceitar cookies
                try:
                    cookie_button = page.locator('button:has-text("Accept"), button:has-text("Aceitar")')
                    if await cookie_button.count() > 0:
                        await cookie_button.first.click()
                        await asyncio.sleep(1)
                except:
                    pass
                
                screenshots = []
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Extrair match_id para o nome do arquivo
                match_id = self.extract_match_id_from_identifier(match_identifier)
                
                # Obter nomes dos times
                try:
                    home_team_element = page.locator('[data-testid="match_header_team_home"] .team-name, .home-team .team-name')
                    away_team_element = page.locator('[data-testid="match_header_team_away"] .team-name, .away-team .team-name')
                    
                    home_team = "Home"
                    away_team = "Away"
                    
                    if await home_team_element.count() > 0:
                        home_team = await home_team_element.first.text_content()
                        home_team = home_team.strip() if home_team else "Home"
                    
                    if await away_team_element.count() > 0:
                        away_team = await away_team_element.first.text_content()
                        away_team = away_team.strip() if away_team else "Away"
                    
                    home_team = "".join(c for c in home_team if c.isalnum() or c in (' ', '-', '_')).strip()
                    away_team = "".join(c for c in away_team if c.isalnum() or c in (' ', '-', '_')).strip()
                    
                except:
                    home_team = "Home"
                    away_team = "Away"
                
                # Tirar screenshot da página principal (overview)
                if 'overview' in sections:
                    filename = f"match_{match_id}_{home_team}_vs_{away_team}_overview_{timestamp}.png"
                    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).strip()
                    filepath = self.prints_dir / filename
                    
                    await page.screenshot(path=str(filepath), full_page=True, type='png')
                    screenshots.append(filepath)
                
                # Navegar para outras seções
                section_selectors = {
                    'statistics': 'a[href*="statistics"], button:has-text("Statistics"), button:has-text("Estatísticas")',
                    'lineups': 'a[href*="lineups"], button:has-text("Lineups"), button:has-text("Escalações")',
                    'timeline': 'a[href*="timeline"], button:has-text("Timeline"), button:has-text("Cronologia")'
                }
                
                for section in sections:
                    if section == 'overview':
                        continue  # Já foi feito
                    
                    if section in section_selectors:
                        try:
                            # Tentar clicar na aba da seção
                            selector = section_selectors[section]
                            tab_element = page.locator(selector)
                            
                            if await tab_element.count() > 0:
                                await tab_element.first.click()
                                await asyncio.sleep(2)  # Aguardar carregar
                                
                                filename = f"match_{match_id}_{home_team}_vs_{away_team}_{section}_{timestamp}.png"
                                filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).strip()
                                filepath = self.prints_dir / filename
                                
                                await page.screenshot(path=str(filepath), full_page=True, type='png')
                                screenshots.append(filepath)
                                
                        except Exception as e:
                            pass
                
                print(f"✅ {len(screenshots)} screenshots salvos com sucesso!")
                return screenshots
                
            except Exception as e:
                print(f"❌ Erro geral: {e}")
                return []
                
            finally:
                await browser.close()

async def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("❌ Uso: python get-print-from-match.py <comando> [argumentos]")
        print("📝 Comandos disponíveis:")
        print("   links                              - Coleta todos os links da página inicial")
        print("   process [arquivo.json]             - Processa JSON e filtra links específicos")
        print("   <match_identifier> [mode]          - Tira screenshots de uma partida")
        print("")
        print("📝 Exemplos:")
        print("   python get-print-from-match.py links")
        print("   python get-print-from-match.py process")
        print("   python get-print-from-match.py process links/all-links_20250611_192400.json")
        print("   python get-print-from-match.py 13970328")
        print("   python get-print-from-match.py independiente-medellin-junior-barranquilla/fxcspxc#id:13970328")
        print("   python get-print-from-match.py independiente-medellin-junior-barranquilla/fxcspxc#id:13970328 multiple")
        print("")
        print("📝 Modes para screenshots:")
        print("   - single (padrão): Screenshot da página completa")
        print("   - multiple: Screenshots de várias seções")
        return
    
    command = sys.argv[1]
    collector = SofaScoreScreenshotCollector()
    
    if command.lower() == "links":
        # Coletar links da página inicial
        print("🚀 Iniciando coleta de links da página inicial...")
        print("=" * 60)
        
        links_data = await collector.get_all_links_from_homepage()
        if links_data:
            print("=" * 60)
            print("✅ Coleta de links concluída com sucesso!")
        else:
            print("❌ Falha na coleta de links")
    
    elif command.lower() == "process":
        # Processar arquivo JSON de links
        print("🚀 Iniciando processamento de links...")
        print("=" * 60)
        
        if len(sys.argv) > 2:
            # Arquivo específico fornecido
            json_file = Path(sys.argv[2])
            if not json_file.exists():
                print(f"❌ Arquivo não encontrado: {json_file}")
                return
        else:
            # Usar arquivo mais recente
            json_file = collector.find_latest_links_file()
            if not json_file:
                return
        
        processed_data = collector.process_links_json(json_file)
        if processed_data:
            print("=" * 60)
            print("✅ Processamento concluído com sucesso!")
            print(f"🔗 Links filtrados: {processed_data['total_filtered_links']}")
        else:
            print("❌ Falha no processamento")
    
    else:
        # Assumir que é um match_identifier para screenshots
        match_identifier = command
        mode = sys.argv[2] if len(sys.argv) > 2 else "single"
        
        print("🚀 Iniciando captura de screenshots...")
        print(f"🆔 Match Identifier: {match_identifier}")
        print(f"🌐 URL construída: {collector.build_match_url(match_identifier)}")
        print(f"📋 Modo: {mode}")
        print("=" * 60)
        
        if mode.lower() == "multiple":
            # Screenshots múltiplos
            screenshots = await collector.take_multiple_screenshots(match_identifier)
            if screenshots:
                print("=" * 60)
                print("✅ Captura múltipla concluída!")
                print(f"📸 Total de screenshots: {len(screenshots)}")
                for screenshot in screenshots:
                    file_size = screenshot.stat().st_size / 1024
                    print(f"   📄 {screenshot.name} ({file_size:.1f} KB)")
            else:
                print("❌ Falha na captura múltipla")
        else:
            # Screenshot único
            screenshot = await collector.take_match_screenshot(match_identifier)
            if screenshot:
                print("=" * 60)
                print("✅ Screenshot capturado com sucesso!")
                file_size = screenshot.stat().st_size / 1024
                print(f"📄 Arquivo: {screenshot.name} ({file_size:.1f} KB)")
            else:
                print("❌ Falha na captura do screenshot")

if __name__ == "__main__":
    asyncio.run(main())
