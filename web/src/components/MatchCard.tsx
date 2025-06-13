import { MatchLink } from '@/types/api';
import { ExternalLink, Brain } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface MatchCardProps {
  match: MatchLink;
}

export default function MatchCard({ match }: MatchCardProps) {
  const router = useRouter();

  const extractTeams = (text: string) => {
    // Remove prefixos de horário e códigos
    let cleanText = text.replace(/^\d{1,2}:\d{2}[A-Z]*\d*/, '').trim();
    
    // Lista de separadores mais comuns em ordem de prioridade
    const separators = [
      ' - ', ' vs ', ' x ', ' VS ', ' X ', 
      'vs', 'VS', 'x', 'X', '-'
    ];
    
    for (const separator of separators) {
      if (cleanText.includes(separator)) {
        const parts = cleanText.split(separator);
        if (parts.length >= 2) {
          const home = parts[0].trim();
          const away = parts[1].trim();
          
          // Verifica se ambos os times têm pelo menos 2 caracteres
          if (home.length >= 2 && away.length >= 2) {
            return { home, away };
          }
        }
      }
    }
    
    // Tenta identificar padrões como "TeamA TeamB" (sem separador explícito)
    const words = cleanText.split(' ');
    if (words.length >= 2) {
      // Se há palavras em maiúscula consecutivas, pode ser dois times
      const upperWords = words.filter(word => word === word.toUpperCase() && word.length > 1);
      if (upperWords.length >= 2) {
        const midPoint = Math.floor(upperWords.length / 2);
        return {
          home: upperWords.slice(0, midPoint).join(' '),
          away: upperWords.slice(midPoint).join(' ')
        };
      }
      
      // Fallback: divide pela metade
      const midPoint = Math.floor(words.length / 2);
      return {
        home: words.slice(0, midPoint).join(' '),
        away: words.slice(midPoint).join(' ')
      };
    }
    
    // Se não conseguir dividir, retorna o texto completo como home
    return { home: cleanText, away: '' };
  };

  const handleAnalysisClick = () => {
    const encodedHref = encodeURIComponent(match.href_original);
    router.push(`/analise-sugestoes?href=${encodedHref}`);
  };

  const teams = extractTeams(match.text);

  return (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 p-4 border">
      {/* Times */}
      <div className="mb-4">
        <div className="flex items-center justify-center space-x-3">
          <div className="text-center flex-1">
            <h3 className="font-semibold text-gray-900 text-sm">{teams.home}</h3>
            <span className="text-xs text-gray-500">Casa</span>
          </div>
          
          {teams.away && (
            <>
              <div className="text-lg font-bold text-gray-400">×</div>
              <div className="text-center flex-1">
                <h3 className="font-semibold text-gray-900 text-sm">{teams.away}</h3>
                <span className="text-xs text-gray-500">Fora</span>
              </div>
            </>
          )}
        </div>
        
        {match.title && (
          <p className="text-xs text-gray-500 text-center mt-2 truncate">{match.title}</p>
        )}
      </div>

      {/* Ações */}
      <div className="flex space-x-2">
        <button
          onClick={handleAnalysisClick}
          className="flex-1 flex items-center justify-center px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
        >
          <Brain className="h-4 w-4 mr-1" />
          Análise
        </button>
        
        <a
          href={match.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
        >
          <ExternalLink className="h-4 w-4 mr-1" />
          SofaScore
        </a>
      </div>

      {/* ID da partida */}
      <div className="mt-3 pt-2 border-t border-gray-100">
        <p className="text-xs text-gray-400 text-center">
          ID: {match.match_id}
        </p>
      </div>
    </div>
  );
} 