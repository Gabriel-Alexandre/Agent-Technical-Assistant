# agent-assistant.py
"""
Assistente Técnico de Futebol Especializado
Analisa dados simplificados e fornece sugestões táticas precisas usando GPT-4o-mini
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class TechnicalAssistant:
    """Assistente Técnico Especializado em Análise Tática"""
    
    def __init__(self):
        # Inicializar cliente OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY não encontrada no arquivo .env")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        
    def load_match_data(self, json_file_path):
        """Carrega dados simplificados da partida"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return None
    
    def create_tactical_prompt(self, match_data):
        """Cria prompt especializado para análise tática"""
        
        # Converter dados para texto estruturado
        match_json = json.dumps(match_data, indent=2, ensure_ascii=False)
        
        prompt = f"""
# ASSISTENTE TÉCNICO ESPECIALIZADO EM FUTEBOL

## PERFIL DO ESPECIALISTA
Você é um **Assistente Técnico de Elite** com 20+ anos de experiência em análise tática, tendo trabalhado com clubes profissionais. Seu conhecimento inclui:

- **Sistemas Táticos**: 4-3-3, 4-2-3-1, 3-5-2, 5-3-2, formações híbridas
- **Transições**: Pressing, contra-pressing, transições rápidas
- **Análise de Vulnerabilidades**: Espaços entre linhas, sobrecarga de flancos
- **Gestão de Jogo**: Controle de ritmo, gestão de vantagem/desvantagem
- **Psicologia Tática**: Pressão, momentum, gestão emocional

## DADOS DA PARTIDA
```json
{match_json}
```

## CRITÉRIOS DE ANÁLISE RIGOROSOS

### ⚠️ IMPORTANTE: SEJA SELETIVO
- **NÃO sugira** mudanças óbvias ou desnecessárias
- **FOQUE** apenas em pontos críticos que podem mudar o resultado
- **BASEIE** todas sugestões em dados concretos
- **PRIORIZE** ajustes que podem ser implementados rapidamente

### 🔍 ANÁLISE TÉCNICA OBRIGATÓRIA

#### 1. ANÁLISE SITUACIONAL
- Como está o **momentum** da partida?
- Qual time está **dominando taticamente**?
- Há **padrões de vulnerabilidade** claros?

#### 2. ANÁLISE ESTATÍSTICA PROFUNDA
- **Eficiência vs Posse**: Qual time é mais efetivo?
- **Zonas de Pressão**: Onde cada time está sendo pressionado?
- **Padrões de Finalização**: Qualidade das chances criadas
- **Solidez Defensiva**: Efetividade nos duelos e tackles

#### 3. ANÁLISE TÁTICA ESPECÍFICA
- **Problemas Estruturais**: Gaps na formação, desbalanceamento
- **Aproveitamento de Flancos**: Efetividade dos cruzamentos
- **Transições**: Velocidade e efetividade nas mudanças de posse
- **Bolas Paradas**: Oportunidades desperdiçadas ou vulnerabilidades

#### 4. GESTÃO DE JOGO
- **Ritmo de Jogo**: Muito rápido/lento para a situação?
- **Gestão de Cartões**: Jogadores em risco
- **Substituições**: Timing e impacto tático

## FORMATO DE RESPOSTA OBRIGATÓRIO

### 📊 SITUAÇÃO TÁTICA ATUAL
[Resumo em 2-3 frases sobre o domínio tático atual]

### 🔍 ANÁLISE CRÍTICA (máximo 4 pontos)
1. **[CATEGORIA]**: Análise específica com dados
2. **[CATEGORIA]**: Análise específica com dados
3. **[CATEGORIA]**: Análise específica com dados
4. **[CATEGORIA]**: Análise específica com dados

### ⚡ SUGESTÕES TÁTICAS PRIORITÁRIAS

#### 🏠 Para Racing de Santander:
**[URGENTE/MÉDIA/BAIXA]** - Sugestão específica com justificativa

#### 🚌 Para Mirandés:
**[URGENTE/MÉDIA/BAIXA]** - Sugestão específica com justificativa

### 🚨 ALERTAS CRÍTICOS
- Riscos iminentes que precisam atenção imediata
- Oportunidades táticas sendo desperdiçadas

### 📈 PREVISÃO TÁTICA
[Como o jogo pode evoluir taticamente nos próximos 15-20 minutos]

## REGRAS DE OURO

✅ **SEMPRE**:
- Use nomes específicos de jogadores
- Cite números exatos das estatísticas
- Explique o "porquê" tático de cada sugestão
- Seja preciso sobre posicionamento e timing

❌ **NUNCA**:
- Sugira mudanças genéricas ("melhorar o ataque")
- Ignore o contexto do placar e tempo de jogo
- Proponha alterações complexas demais
- Seja superficial nas análises

---

## ANÁLISE: Forneça sua avaliação técnica seguindo EXATAMENTE este formato."""

        return prompt
    
    def analyze_match(self, match_data):
        """Realiza análise tática usando GPT-4o-mini"""
        try:
            print("🤖 Iniciando análise tática especializada...")
            
            # Criar prompt especializado
            prompt = self.create_tactical_prompt(match_data)
            
            # Fazer chamada para GPT-4o-mini
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Você é um assistente técnico de futebol especializado com vasta experiência em análise tática profissional."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Baixa temperatura para análises mais precisas
                max_tokens=2000,
                top_p=0.9
            )
            
            analysis = response.choices[0].message.content
            
            print("✅ Análise concluída!")
            return analysis
            
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            return None
    
    def analyze_match_with_prompt(self, custom_prompt):
        """Realiza análise tática usando prompt personalizado"""
        try:
            print("🤖 Iniciando análise tática com prompt personalizado...")
            
            # Fazer chamada para GPT-4o-mini com prompt personalizado
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Você é um especialista em análise tática de futebol com 20 anos de experiência. Forneça análises diretas, práticas e específicas baseadas nos dados fornecidos."
                    },
                    {
                        "role": "user", 
                        "content": custom_prompt
                    }
                ],
                temperature=0.2,  # Temperatura ainda mais baixa para análises diretas
                max_tokens=1500,
                top_p=0.8
            )
            
            analysis = response.choices[0].message.content
            
            print("✅ Análise personalizada concluída!")
            return analysis
            
        except Exception as e:
            print(f"❌ Erro na análise personalizada: {e}")
            return None
    
    def analyze_image_with_prompt(self, custom_prompt, image_base64):
        """Realiza análise tática visual usando imagem"""
        try:
            print("🤖 Iniciando análise tática visual com imagem...")
            
            # Fazer chamada para GPT-4o-mini com análise de imagem
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Modelo que suporta visão
                messages=[
                    {
                        "role": "system", 
                        "content": "Você é um especialista em análise tática de futebol com 20 anos de experiência. Analise a imagem fornecida e forneça análises diretas, práticas e específicas baseadas no que consegue ver."
                    },
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": custom_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.2,
                max_tokens=2000,
                top_p=0.8
            )
            
            analysis = response.choices[0].message.content
            
            print("✅ Análise visual concluída!")
            return analysis
            
        except Exception as e:
            print(f"❌ Erro na análise visual: {e}")
            # Fallback para análise sem imagem
            print("🔄 Tentando análise sem imagem como fallback...")
            return self.analyze_match_with_prompt(custom_prompt)
    
    def save_analysis(self, analysis, original_file_path):
        """Salva análise em arquivo"""
        if not analysis:
            return None
            
        try:
            # Criar nome do arquivo de análise
            original_path = Path(original_file_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            analysis_filename = f"analysis_{original_path.stem}_{timestamp}.md"
            analysis_path = original_path.parent / analysis_filename
            
            with open(analysis_path, 'w', encoding='utf-8') as f:
                f.write(f"# Análise Técnica - {timestamp}\n\n")
                f.write(f"**Arquivo Analisado**: {original_path.name}\n\n")
                f.write("---\n\n")
                f.write(analysis)
            
            print(f"📄 Análise salva em: {analysis_path.absolute()}")
            return analysis_path
            
        except Exception as e:
            print(f"❌ Erro ao salvar análise: {e}")
            return None
    
    def display_analysis(self, analysis):
        """Exibe análise formatada no terminal"""
        print("\n" + "="*80)
        print("🏆 ANÁLISE TÉCNICA ESPECIALIZADA")
        print("="*80)
        print(analysis)
        print("="*80)

def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("❌ Uso: python agent-assistant.py <caminho_do_json_simplificado>")
        print("📝 Exemplo: python agent-assistant.py live_data_simplify/simplified_match_13963638_20250608_144908.json")
        return
    
    json_file_path = sys.argv[1]
    
    # Verificar se arquivo existe
    if not Path(json_file_path).exists():
        print(f"❌ Arquivo não encontrado: {json_file_path}")
        return
    
    # Verificar se é arquivo simplificado
    if "simplified_" not in Path(json_file_path).name:
        print("⚠️  AVISO: Este arquivo não parece ser um JSON simplificado.")
        print("📋 Recomendado usar arquivos da pasta 'live_data_simplify/'")
    
    try:
        print(f"🚀 Iniciando análise técnica de: {json_file_path}")
        print("="*60)
        
        # Inicializar assistente
        assistant = TechnicalAssistant()
        
        # Carregar dados
        match_data = assistant.load_match_data(json_file_path)
        if not match_data:
            return
        
        # Extrair informações básicas
        home_team = match_data.get('match_summary', {}).get('home_team', 'Time Casa')
        away_team = match_data.get('match_summary', {}).get('away_team', 'Time Visitante')
        score = match_data.get('match_summary', {}).get('score', {})
        status = match_data.get('match_summary', {}).get('status', 'Desconhecido')
        
        print(f"⚽ {home_team} {score.get('home', 0)} x {score.get('away', 0)} {away_team}")
        print(f"📊 Status: {status}")
        print("="*60)
        
        # Realizar análise
        analysis = assistant.analyze_match(match_data)
        
        if analysis:
            # Exibir análise
            assistant.display_analysis(analysis)
            
            # Salvar análise
            assistant.save_analysis(analysis, json_file_path)
            
            print("\n🎯 ANÁLISE CONCLUÍDA!")
            print("💡 Use essas informações para tomar decisões táticas informadas.")
        else:
            print("❌ Falha na análise técnica")
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()
