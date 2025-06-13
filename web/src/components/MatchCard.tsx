import { MatchLink } from '@/types/api';
import { ExternalLink, Brain } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface MatchCardProps {
  match: MatchLink;
}

export default function MatchCard({ match }: MatchCardProps) {
  const router = useRouter();

  const extractTeams = (text: string) => {
    // Tenta diferentes separadores comuns
    const separators = [' - ', ' vs ', ' x ', 'vs'];
    
    for (const separator of separators) {
      if (text.includes(separator)) {
        const parts = text.split(separator);
        if (parts.length === 2) {
          return { home: parts[0].trim(), away: parts[1].trim() };
        }
      }
    }
    
    // Se não encontrar separador, retorna o texto completo como home
    return { home: text, away: '' };
  };

  const handleAnalysisClick = () => {
    // Usar encodeURIComponent para tratar caracteres especiais corretamente
    const encodedHref = encodeURIComponent(match.href_original);
    router.push(`/analise-sugestoes?href=${encodedHref}`);
  };

  const teams = extractTeams(match.text);

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 p-6">
      {/* Header com times */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center justify-center space-x-4">
            <div className="text-center">
              <h3 className="font-bold text-lg text-gray-900">{teams.home}</h3>
            </div>
            {teams.away && (
              <>
                <div className="text-2xl font-bold text-gray-400">VS</div>
                <div className="text-center">
                  <h3 className="font-bold text-lg text-gray-900">{teams.away}</h3>
                </div>
              </>
            )}
          </div>
          {match.title && (
            <p className="text-sm text-gray-600 text-center mt-2">{match.title}</p>
          )}
        </div>
      </div>

      {/* Ações */}
      <div className="flex space-x-3">
        <button
          onClick={handleAnalysisClick}
          className="flex-1 flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          <Brain className="h-4 w-4 mr-2" />
          Análise de Sugestões
        </button>
        
        <a
          href={match.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <ExternalLink className="h-4 w-4 mr-2" />
          SofaScore
        </a>
      </div>

      {/* Match ID para referência */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        <p className="text-xs text-gray-400">
          ID: {match.match_id}
        </p>
      </div>
    </div>
  );
} 