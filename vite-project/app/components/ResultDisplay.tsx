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
    <div className="mt-4 sm:mt-6 space-y-4 sm:space-y-6">
      {/* Result Header */}
      <div className={`
        rounded-lg p-4 sm:p-6 text-center
        ${answer.isCorrect 
          ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' 
          : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
        }
      `}>
        {getResultIcon()}
        <h3 className={`
          text-responsive-xl font-bold mb-3 sm:mb-4
          ${answer.isCorrect ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'}
        `}>
          {answer.isCorrect ? '正解！' : '不正解'}
        </h3>
        
        <div className="space-y-2 sm:space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-center gap-1 sm:gap-4">
            <div className="flex items-center justify-center">
              <span className="font-medium text-gray-700 dark:text-gray-300 text-responsive-sm">あなたの回答:</span>
              <span className={`ml-2 font-bold text-responsive-sm ${answer.isCorrect ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'}`}>
                {getUserAnswerText()}
              </span>
            </div>
            {!answer.isCorrect && (
              <div className="flex items-center justify-center">
                <span className="font-medium text-gray-700 dark:text-gray-300 text-responsive-sm">正解:</span>
                <span className="ml-2 font-bold text-green-700 dark:text-green-300 text-responsive-sm">
                  {getCorrectAnswerText()}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Options with Explanations */}
      <div className="card-base bg-gray-50 dark:bg-gray-800/50">
        <h4 className="font-bold text-lg text-gray-900 dark:text-white mb-4 border-b border-gray-300 dark:border-gray-600 pb-2">
          <span className="text-gray-800 dark:text-gray-100">選択肢の解説</span>
        </h4>
        <div className="space-y-2 sm:space-y-3">
          {question.options.map((option, index) => {
            const explanation = getExplanationForOption(option);
            if (!explanation) return null;

            return (
              <div key={index} className="flex items-start space-x-2 sm:space-x-3 p-2 sm:p-3 bg-white dark:bg-gray-700 rounded-lg">
                <span className={`
                  inline-flex items-center px-2 py-1 text-xs font-medium rounded-full flex-shrink-0
                  ${explanation.includes('✓') 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  }
                `}>
                  {explanation.includes('✓') ? (
                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  )}
                  {explanation.includes('✓') ? '正解' : '不正解'}
                </span>
                <span className="text-gray-700 dark:text-gray-300 text-responsive-sm leading-relaxed">
                  {option}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Detailed Explanation */}
      <div className="card-base">
        <h4 className="font-bold text-lg text-gray-900 dark:text-white mb-4 flex items-center border-b border-gray-200 dark:border-gray-600 pb-2">
          <svg className="w-5 h-5 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-blue-900 dark:text-blue-100">詳細解説</span>
        </h4>
        <div className="prose prose-sm sm:prose-base max-w-none dark:prose-invert">
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-responsive-sm">
            {question.explanation}
          </p>
        </div>
      </div>

      {/* Learning Resources */}
      {question.learningResources && question.learningResources.length > 0 && (
        <div className="card-base bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <h4 className="font-bold text-lg text-blue-900 dark:text-blue-200 mb-4 flex items-center border-b border-blue-300 dark:border-blue-700 pb-2">
            <svg className="w-5 h-5 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <span className="text-blue-800 dark:text-blue-100">学習リソース</span>
          </h4>
          <div className="space-y-2 sm:space-y-3">
            {question.learningResources.map((resource, index) => (
              <div key={index} className="flex items-start space-x-2 sm:space-x-3 p-2 sm:p-3 bg-white dark:bg-blue-800/30 rounded-lg">
                <span className={`
                  inline-flex items-center px-2 py-1 text-xs font-medium rounded-full flex-shrink-0
                  ${resource.type === 'documentation' ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200' :
                    resource.type === 'blog' ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200' :
                    resource.type === 'video' ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                  }
                `}>
                  {resource.type === 'documentation' ? '📚' :
                   resource.type === 'blog' ? '📝' :
                   resource.type === 'video' ? '🎥' : '📄'}
                  <span className="ml-1 hidden sm:inline">
                    {resource.type === 'documentation' ? 'ドキュメント' :
                     resource.type === 'blog' ? 'ブログ' :
                     resource.type === 'video' ? '動画' : '資料'}
                  </span>
                </span>
                <div className="flex-1 min-w-0">
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-700 dark:text-blue-300 hover:text-blue-900 dark:hover:text-blue-100 font-medium text-responsive-sm hover:underline block truncate"
                  >
                    {resource.title}
                  </a>
                  {resource.description && (
                    <p className="text-gray-600 dark:text-gray-400 text-responsive-xs mt-1 line-clamp-2">
                      {resource.description}
                    </p>
                  )}
                </div>
                <svg className="w-3 h-3 sm:w-4 sm:h-4 text-gray-400 dark:text-gray-500 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Related Services */}
      {question.relatedServices && question.relatedServices.length > 0 && (
        <div className="card-base bg-gray-50 dark:bg-gray-800/50">
          <h5 className="font-bold text-base text-gray-900 dark:text-white mb-3 border-b border-gray-300 dark:border-gray-600 pb-2">
            <span className="text-gray-800 dark:text-gray-100">関連サービス</span>
          </h5>
          <div className="flex flex-wrap gap-1 sm:gap-2">
            {question.relatedServices.map((service, index) => (
              <span
                key={index}
                className="inline-flex items-center bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs px-2 py-1 rounded-full"
              >
                <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
                {service}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Next Button */}
      {showNextButton && (
        <div className="flex flex-col sm:flex-row justify-center gap-3 pt-2 sm:pt-4">
          <button
            onClick={onNext}
            className="btn-primary w-full sm:w-auto px-6 sm:px-8 py-3 hover:shadow-lg active:scale-95"
            aria-label="次の問題に進む"
          >
            <span className="flex items-center justify-center">
              次の問題
              <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </span>
          </button>
        </div>
      )}
    </div>
  );
}