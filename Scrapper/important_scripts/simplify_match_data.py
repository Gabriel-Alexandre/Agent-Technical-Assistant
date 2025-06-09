# simplify_match_data.py
"""
Simplifica dados complexos do SofaScore para análise por IA
Extrai apenas informações relevantes para assistente técnico
"""

import json
import sys
from pathlib import Path
from datetime import datetime

class MatchDataSimplifier:
    """Simplifica dados de partida para análise por IA"""
    
    def __init__(self):
        pass
    
    def extract_key_statistics(self, stats_data):
        """Extrai estatísticas principais organizadas por categoria"""
        simplified_stats = {
            "possession": {},
            "shots": {},
            "passes": {},
            "duels": {},
            "defending": {}
        }
        
        if not stats_data:
            return simplified_stats
            
        for period_data in stats_data:
            if period_data.get("period") == "ALL":
                groups = period_data.get("groups", [])
                
                for group in groups:
                    group_name = group.get("groupName", "").lower()
                    items = group.get("statisticsItems", [])
                    
                    for item in items:
                        name = item.get("name", "")
                        home = item.get("home", "0")
                        away = item.get("away", "0")
                        
                        # Categorizar estatísticas
                        if "possession" in name.lower():
                            simplified_stats["possession"][name] = {"home": home, "away": away}
                        elif any(word in name.lower() for word in ["shot", "goal", "chance"]):
                            simplified_stats["shots"][name] = {"home": home, "away": away}
                        elif any(word in name.lower() for word in ["pass", "cross", "through"]):
                            simplified_stats["passes"][name] = {"home": home, "away": away}
                        elif any(word in name.lower() for word in ["duel", "aerial", "ground"]):
                            simplified_stats["duels"][name] = {"home": home, "away": away}
                        elif any(word in name.lower() for word in ["tackle", "clearance", "block"]):
                            simplified_stats["defending"][name] = {"home": home, "away": away}
        
        return simplified_stats
    
    def extract_goals_and_events(self, timeline_data):
        """Extrai gols e eventos principais"""
        events = {
            "goals": [],
            "cards": [],
            "substitutions": [],
            "key_moments": []
        }
        
        if not timeline_data:
            return events
            
        for incident in timeline_data:
            incident_type = incident.get("incidentType", "")
            time = incident.get("time", 0)
            is_home = incident.get("isHome", False)
            team = "home" if is_home else "away"
            
            if incident_type == "goal":
                player_name = incident.get("player", {}).get("name", "Desconhecido")
                assist_name = incident.get("assist1", {}).get("name", "")
                
                events["goals"].append({
                    "time": time,
                    "team": team,
                    "player": player_name,
                    "assist": assist_name,
                    "type": incident.get("goalType", "regular")
                })
                
            elif incident_type in ["card", "yellowCard", "redCard"]:
                player_name = incident.get("player", {}).get("name", "Desconhecido")
                events["cards"].append({
                    "time": time,
                    "team": team,
                    "player": player_name,
                    "type": incident_type
                })
                
            elif incident_type == "substitution":
                player_in = incident.get("playerIn", {}).get("name", "")
                player_out = incident.get("playerOut", {}).get("name", "")
                events["substitutions"].append({
                    "time": time,
                    "team": team,
                    "player_in": player_in,
                    "player_out": player_out
                })
        
        return events
    
    def extract_formations_and_lineups(self, lineups_data):
        """Extrai formações e escalações principais"""
        formations = {
            "home": {"formation": "", "key_players": []},
            "away": {"formation": "", "key_players": []}
        }
        
        if not lineups_data:
            return formations
            
        for team_key in ["home", "away"]:
            team_data = lineups_data.get(team_key, {})
            formations[team_key]["formation"] = team_data.get("formation", "")
            
            players = team_data.get("players", [])
            for player_data in players:
                if not player_data.get("substitute", False):  # Apenas titulares
                    player = player_data.get("player", {})
                    formations[team_key]["key_players"].append({
                        "name": player.get("name", ""),
                        "position": player.get("position", ""),
                        "jersey": player.get("jerseyNumber", ""),
                        "rating": player_data.get("statistics", {}).get("rating", 0)
                    })
        
        return formations
    
    def extract_shot_analysis(self, shotmap_data):
        """Analisa padrões de chutes"""
        shot_analysis = {
            "total_shots": {"home": 0, "away": 0},
            "goals": {"home": 0, "away": 0},
            "shot_locations": {"home": [], "away": []},
            "shooting_efficiency": {"home": "0%", "away": "0%"}
        }
        
        if not shotmap_data:
            return shot_analysis
            
        for shot in shotmap_data:
            is_home = shot.get("isHome", False)
            team_key = "home" if is_home else "away"
            shot_type = shot.get("shotType", "")
            
            shot_analysis["total_shots"][team_key] += 1
            
            if shot_type == "goal":
                shot_analysis["goals"][team_key] += 1
            
            # Analisar localização do chute
            coords = shot.get("playerCoordinates", {})
            if coords:
                x, y = coords.get("x", 0), coords.get("y", 0)
                location = "box" if x > 83 else "outside_box"
                shot_analysis["shot_locations"][team_key].append({
                    "time": shot.get("time", 0),
                    "location": location,
                    "result": shot_type
                })
        
        # Calcular eficiência
        for team in ["home", "away"]:
            total = shot_analysis["total_shots"][team]
            goals = shot_analysis["goals"][team]
            if total > 0:
                efficiency = (goals / total) * 100
                shot_analysis["shooting_efficiency"][team] = f"{efficiency:.1f}%"
        
        return shot_analysis
    
    def simplify_match_data(self, json_file_path):
        """Função principal para simplificar dados da partida"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                full_data = json.load(f)
            
            # Extrair informações básicas
            basic_info = full_data.get("basic_info", {})
            
            simplified_data = {
                "match_summary": {
                    "home_team": basic_info.get("homeTeam", {}).get("name", ""),
                    "away_team": basic_info.get("awayTeam", {}).get("name", ""),
                    "score": {
                        "home": basic_info.get("homeScore", {}).get("current", 0),
                        "away": basic_info.get("awayScore", {}).get("current", 0)
                    },
                    "status": basic_info.get("status", {}).get("description", ""),
                    "tournament": basic_info.get("tournament", {}).get("name", ""),
                    "managers": {
                        "home": basic_info.get("homeTeam", {}).get("manager", {}).get("name", ""),
                        "away": basic_info.get("awayTeam", {}).get("manager", {}).get("name", "")
                    }
                },
                
                "key_statistics": self.extract_key_statistics(full_data.get("statistics", [])),
                
                "events_timeline": self.extract_goals_and_events(full_data.get("timeline", [])),
                
                "tactical_setup": self.extract_formations_and_lineups(full_data.get("lineups", {})),
                
                "shooting_analysis": self.extract_shot_analysis(full_data.get("shotmap", [])),
                
                "collection_info": {
                    "collected_at": full_data.get("metadata", {}).get("collected_at", ""),
                    "match_id": full_data.get("metadata", {}).get("match_id", "")
                }
            }
            
            return simplified_data
            
        except Exception as e:
            print(f"❌ Erro ao processar arquivo: {e}")
            return None
    
    def save_simplified_data(self, simplified_data, original_file_path):
        """Salva dados simplificados"""
        if not simplified_data:
            return None
            
        # Criar nome do arquivo simplificado
        original_path = Path(original_file_path)
        simplified_filename = f"simplified_{original_path.stem}.json"
        simplified_path = original_path.parent / simplified_filename
        
        try:
            with open(simplified_path, 'w', encoding='utf-8') as f:
                json.dump(simplified_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Dados simplificados salvos em: {simplified_path.absolute()}")
            return simplified_path
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo simplificado: {e}")
            return None

def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("❌ Uso: python simplify_match_data.py <caminho_do_arquivo_json>")
        print("📝 Exemplo: python simplify_match_data.py live_data/match_13963638_20250608_143417.json")
        return
    
    json_file_path = sys.argv[1]
    
    if not Path(json_file_path).exists():
        print(f"❌ Arquivo não encontrado: {json_file_path}")
        return
    
    print(f"🔄 Simplificando dados de: {json_file_path}")
    print("=" * 60)
    
    simplifier = MatchDataSimplifier()
    simplified_data = simplifier.simplify_match_data(json_file_path)
    
    if simplified_data:
        saved_path = simplifier.save_simplified_data(simplified_data, json_file_path)
        if saved_path:
            print("=" * 60)
            print("✅ Simplificação concluída com sucesso!")
            print(f"📊 Arquivo original: {Path(json_file_path).stat().st_size / 1024:.1f} KB")
            print(f"📊 Arquivo simplificado: {saved_path.stat().st_size / 1024:.1f} KB")
            print(f"📉 Redução: {((Path(json_file_path).stat().st_size - saved_path.stat().st_size) / Path(json_file_path).stat().st_size * 100):.1f}%")
    else:
        print("❌ Falha na simplificação")

if __name__ == "__main__":
    main() 