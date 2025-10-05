import type { Question, Answer } from '~/types';

interface ResultDisplayProps {
  question: Question;
  answer: Answer;
  onNext: () => void;
  showNextButton?: boolean;
}

export function ResultDisplay({ 
  question, 
  answer, 
  onNext, 
  showNextButton = true 
}: ResultDisplayProps) {
  const getCorrectAnswerText = (): string => {
    if (question.type === 'single') {
      return Array.isArray(answer.correctAnswer) 
        ? answer.correctAnswer[0] 
        : answer.correctAnswer;
    } else {
      const correctAnswers = Array.isArray(answer.correctAnswer) 
        ? answer.correctAnswer 
        : [answer.correctAnswer];
      return correctAnswers.join(', ');
    }
  };

  const getUserAnswerText = (): string => {
    if (question.type === 'single') {
      return Array.isArray(answer.userAnswer) 
        ? answer.userAnswer[0] 
        : answer.userAnswer;
    } else {
      const userAnswers = Array.isArray(answer.userAnswer) 
        ? answer.userAnswer 
        : [answer.userAnswer];
      return userAnswers.join(', ');
    }
  };

  const getResultIcon = () => {
    if (answer.isCorrect) {
      return (
        <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-4">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      );
    } else {
      return (
        <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-full mb-4">
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
      );
    }
  };

  const getExplanationForOption = (option: string): string | null => {
    // Extract option letter
    const optionLetter = option.match(/^([A-Z])\./)?.[1];
    if (!optionLetter) return null;

    const correctAnswers = Array.isArray(answer.correctAnswer) 
      ? answer.correctAnswer 
      : [answer.correctAnswer];
    
    const userAnswers = Array.isArray(answer.userAnswer) 
      ? answer.userAnswer 
      : [answer.userAnswer];

    if (correctAnswers.includes(optionLetter)) {
      return '✓ 正解';
    } else if (userAnswers.includes(optionLetter)) {
      return '✗ 不正解';
    }
    
    return null;
  };

  return (
    <div className="mt-6 space-y-6">
      {/* Result Header */}
      <div className={`
        rounded-lg p-6 text-center
        ${answer.isCorrect ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}
      `}>
        {getResultIcon()}
        <h3 className={`
          text-2xl font-bold mb-2
          ${answer.isCorrect ? 'text-green-800' : 'text-red-800'}
        `}>
          {answer.isCorrect ? '正解！' : '不正解'}
        </h3>
        
        <div className="space-y-2 text-sm">
          <div>
            <span className="font-medium text-gray-700">あなたの回答: </span>
            <span className={`font-semibold ${answer.isCorrect ? 'text-green-700' : 'text-red-700'}`}>
              {getUserAnswerText()}
            </span>
          </div>
          {!answer.isCorrect && (
            <div>
              <span className="font-medium text-gray-700">正解: </span>
              <span className="font-semibold text-green-700">
                {getCorrectAnswerText()}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Options with Explanations */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h4 className="font-semibold text-gray-900 mb-4">選択肢の解説</h4>
        <div className="space-y-3">
          {question.options.map((option, index) => {
            const explanation = getExplanationForOption(option);
            if (!explanation) return null;

            return (
              <div key={index} className="flex items-start space-x-3">
                <span className={`
                  inline-block px-2 py-1 text-xs font-medium rounded
                  ${explanation.includes('✓') 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                  }
                `}>
                  {explanation}
                </span>
                <span className="text-gray-700 text-sm">
                  {option}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Detailed Explanation */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
          <svg className="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          詳細解説
        </h4>
        <div className="prose prose-sm max-w-none">
          <p className="text-gray-700 leading-relaxed">
            {question.explanation}
          </p>
        </div>
      </div>

      {/* Learning Resources */}
      {question.learningResources && question.learningResources.length > 0 && (
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
          <h4 className="font-semibold text-blue-900 mb-4 flex items-center">
            <svg className="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            学習リソース
          </h4>
          <div className="space-y-3">
            {question.learningResources.map((resource, index) => (
              <div key={index} className="flex items-start space-x-3">
                <span className={`
                  inline-block px-2 py-1 text-xs font-medium rounded
                  ${resource.type === 'documentation' ? 'bg-blue-100 text-blue-800' :
                    resource.type === 'blog' ? 'bg-green-100 text-green-800' :
                    resource.type === 'video' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }
                `}>
                  {resource.type === 'documentation' ? '📚 ドキュメント' :
                   resource.type === 'blog' ? '📝 ブログ' :
                   resource.type === 'video' ? '🎥 動画' :
                   '📄 資料'
                  }
                </span>
                <div className="flex-1">
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-700 hover:text-blue-900 font-medium text-sm hover:underline"
                  >
                    {resource.title}
                  </a>
                  {resource.description && (
                    <p className="text-gray-600 text-xs mt-1">
                      {resource.description}
                    </p>
                  )}
                </div>
                <svg className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Related Services */}
      {question.relatedServices && question.relatedServices.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h5 className="font-medium text-gray-900 mb-2 text-sm">関連サービス:</h5>
          <div className="flex flex-wrap gap-2">
            {question.relatedServices.map((service, index) => (
              <span
                key={index}
                className="inline-block bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded"
              >
                {service}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Next Button */}
      {showNextButton && (
        <div className="flex justify-center pt-4">
          <button
            onClick={onNext}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center space-x-2"
          >
            <span>次の問題</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}