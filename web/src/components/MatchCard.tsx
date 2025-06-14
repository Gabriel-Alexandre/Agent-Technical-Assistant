import { DetailedMatch } from '@/types/api';
import { ExternalLink, Brain, Clock, Play, Square, CheckCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface MatchCardProps {
  match: DetailedMatch;
}

export default function MatchCard({ match }: MatchCardProps) {
  const router = useRouter();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in_progress':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'not_started':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'finished':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'postponed':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'in_progress':
        return <Play className="h-3 w-3" />;
      case 'not_started':
        return <Clock className="h-3 w-3" />;
      case 'finished':
        return <CheckCircle className="h-3 w-3" />;
      case 'postponed':
        return <Square className="h-3 w-3" />;
      default:
        return <Square className="h-3 w-3" />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'in_progress':
        return 'Ao Vivo';
      case 'not_started':
        return 'Não Iniciado';
      case 'finished':
        return 'Finalizado';
      case 'postponed':
        return 'Adiado';
      default:
        return status;
    }
  };

  const isPostponed = match.home_score === 'Adiado' && match.away_score === 'Adiado';
  const showScore = !isPostponed && match.match_status !== 'not_started';

  const handleAnalysisClick = () => {
    const encodedHref = encodeURIComponent(match.url);
    router.push(`/analise-sugestoes?href=${encodedHref}`);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 p-4 border">
      {/* Status */}
      <div className="mb-3">
        <div className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(match.match_status)}`}>
          {getStatusIcon(match.match_status)}
          <span>{getStatusLabel(match.match_status)}</span>
          {match.match_status === 'in_progress' && (
            <span className="ml-1">• {match.match_time}</span>
          )}
        </div>
        {match.match_status === 'not_started' && (
          <div className="text-xs text-gray-500 mt-1">
            {match.match_time}
          </div>
        )}
      </div>

      {/* Times e Placar */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 text-sm truncate">{match.home_team}</h3>
            <span className="text-xs text-gray-500">Casa</span>
          </div>
          
          {showScore && (
            <div className="mx-4 text-center">
              <div className="text-lg font-bold text-gray-900">
                {match.home_score} - {match.away_score}
              </div>
            </div>
          )}
          
          {!showScore && (
            <div className="mx-4 text-center">
              <div className="text-lg font-bold text-gray-400">vs</div>
            </div>
          )}
          
          <div className="flex-1 text-right">
            <h3 className="font-semibold text-gray-900 text-sm truncate">{match.away_team}</h3>
            <span className="text-xs text-gray-500">Fora</span>
          </div>
        </div>
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
    </div>
  );
} 