import { ScreenshotAnalysis } from '@/types/api';
import { Clock, ExternalLink, Image, FileText } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useState } from 'react';

interface AnalysisCardProps {
  analysis: ScreenshotAnalysis;
}

export default function AnalysisCard({ analysis }: AnalysisCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatAnalysisTime = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { 
        addSuffix: true, 
        locale: ptBR 
      });
    } catch {
      return 'Tempo indisponível';
    }
  };

  const formatAnalysisText = (text: string) => {
    // Converter markdown básico para HTML
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br />');
  };

  const getPreviewText = (text: string, maxLength: number = 200) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 p-6">
      {/* Header com times */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center justify-center space-x-4">
            <div className="text-center">
              <h3 className="font-bold text-lg text-gray-900">{analysis.home_team}</h3>
            </div>
            <div className="text-2xl font-bold text-gray-400">VS</div>
            <div className="text-center">
              <h3 className="font-bold text-lg text-gray-900">{analysis.away_team}</h3>
            </div>
          </div>
        </div>
      </div>

      {/* Informações da análise */}
      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
        <div className="flex items-center">
          <Clock className="h-4 w-4 mr-1" />
          <span>{formatAnalysisTime(analysis.created_at)}</span>
        </div>
        <div className="flex items-center space-x-2">
                     {analysis.screenshot_filename && (
             <div className="flex items-center text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
               <Image className="h-3 w-3 mr-1" />
               Screenshot
             </div>
           )}
          <div className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
            <FileText className="h-3 w-3 mr-1 inline" />
            Análise IA
          </div>
        </div>
      </div>

      {/* Prévia da análise */}
      <div className="mb-4">
        <div 
          className="text-sm text-gray-700 leading-relaxed"
          dangerouslySetInnerHTML={{ 
            __html: formatAnalysisText(
              isExpanded ? analysis.analysis_text : getPreviewText(analysis.analysis_text)
            ) 
          }}
        />
        
        {analysis.analysis_text.length > 200 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-2 text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            {isExpanded ? 'Ver menos' : 'Ver mais'}
          </button>
        )}
      </div>

      {/* Ações */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div className="text-xs text-gray-400">
          ID: {analysis.match_id}
        </div>
        
        <div className="flex space-x-2">
          <a
            href={analysis.match_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
          >
            <ExternalLink className="h-3 w-3 mr-1" />
            Ver Partida
          </a>
        </div>
      </div>
    </div>
  );
} 