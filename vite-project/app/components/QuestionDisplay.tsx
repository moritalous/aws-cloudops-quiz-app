import type { Question } from '~/types';

interface QuestionDisplayProps {
  question: Question;
  selectedAnswer: string | string[];
  onAnswerSelect: (answer: string | string[]) => void;
  onSubmit: () => void;
  showResult: boolean;
  disabled?: boolean;
}

export function QuestionDisplay({
  question,
  selectedAnswer,
  onAnswerSelect,
  onSubmit,
  showResult,
  disabled = false
}: QuestionDisplayProps) {
  const handleSingleAnswerSelect = (value: string) => {
    if (disabled || showResult) return;
    onAnswerSelect(value);
  };

  const handleMultipleAnswerSelect = (value: string) => {
    if (disabled || showResult) return;
    
    const currentAnswers = Array.isArray(selectedAnswer) ? selectedAnswer : [];
    const newAnswers = currentAnswers.includes(value)
      ? currentAnswers.filter(answer => answer !== value)
      : [...currentAnswers, value];
    
    onAnswerSelect(newAnswers);
  };

  const isAnswerSelected = (optionValue: string): boolean => {
    if (question.type === 'single') {
      return selectedAnswer === optionValue;
    } else {
      return Array.isArray(selectedAnswer) && selectedAnswer.includes(optionValue);
    }
  };

  const isSubmitDisabled = (): boolean => {
    if (disabled || showResult) return true;
    
    if (question.type === 'single') {
      return !selectedAnswer;
    } else {
      return !Array.isArray(selectedAnswer) || selectedAnswer.length === 0;
    }
  };

  const getOptionLetter = (option: string): string => {
    // Extract letter from option (e.g., "A. CloudWatch" -> "A")
    const match = option.match(/^([A-Z])\./);
    return match ? match[1] : option.charAt(0);
  };

  return (
    <div className="card-base touch-friendly">
      {/* Question Header */}
      <header className="mb-4 sm:mb-6">
        <div className="flex flex-wrap gap-2 mb-3 sm:mb-4">
          <span className="inline-flex items-center px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            <svg className="w-3 h-3 sm:w-4 sm:h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
            </svg>
            {question.domain}
          </span>
          <span className={`inline-flex items-center px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium ${
            question.difficulty === 'easy' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
            question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
            'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            <svg className="w-3 h-3 sm:w-4 sm:h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            {question.difficulty === 'easy' ? '初級' : question.difficulty === 'medium' ? '中級' : '上級'}
          </span>
          <span className="inline-flex items-center px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
            <svg className="w-3 h-3 sm:w-4 sm:h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {question.type === 'single' ? '単一回答' : '複数回答'}
          </span>
        </div>
        
        <h2 className="text-responsive-lg font-semibold text-gray-900 dark:text-white leading-relaxed mb-3">
          {question.question}
        </h2>
        
        {question.type === 'multiple' && (
          <div className="flex items-center p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
            <svg className="w-5 h-5 text-amber-600 dark:text-amber-400 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-amber-800 dark:text-amber-200">
                複数の選択肢を選択してください
              </p>
              {Array.isArray(selectedAnswer) && selectedAnswer.length > 0 && (
                <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">
                  選択済み: {selectedAnswer.length}個
                </p>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Options */}
      <div className="space-y-2 sm:space-y-3 mb-6" role="group" aria-labelledby="question-options">
        <div id="question-options" className="sr-only">回答選択肢</div>
        {question.options.map((option, index) => {
          const optionValue = getOptionLetter(option);
          const isSelected = isAnswerSelected(optionValue);
          
          return (
            <label
              key={index}
              className={`
                flex items-start p-3 sm:p-4 border rounded-lg cursor-pointer transition-all duration-200 touch-friendly
                ${isSelected 
                  ? question.type === 'multiple'
                    ? 'border-green-500 bg-green-50 dark:bg-green-900/20 dark:border-green-400 shadow-sm'
                    : 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400 shadow-sm'
                  : 'border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                }
                ${(disabled || showResult) ? 'cursor-not-allowed opacity-60' : 'hover:shadow-sm active:scale-95'}
              `}
            >
              <input
                type={question.type === 'single' ? 'radio' : 'checkbox'}
                name={question.type === 'single' ? `question-${question.id}` : `answer-${question.id}`}
                value={optionValue}
                checked={isSelected}
                onChange={() => {
                  if (question.type === 'single') {
                    handleSingleAnswerSelect(optionValue);
                  } else {
                    handleMultipleAnswerSelect(optionValue);
                  }
                }}
                disabled={disabled || showResult}
                className={`
                  mt-0.5 sm:mt-1 mr-3 flex-shrink-0 w-4 h-4 sm:w-5 sm:h-5
                  ${question.type === 'single' 
                    ? 'text-blue-600 focus:ring-blue-500 focus:ring-2' 
                    : 'text-blue-600 focus:ring-blue-500 focus:ring-2 rounded'
                  }
                  ${(disabled || showResult) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                `}
                aria-describedby={`option-${index}-text`}
              />
              <span 
                id={`option-${index}-text`}
                className="text-responsive-sm text-gray-900 dark:text-gray-100 leading-relaxed"
              >
                {option}
              </span>
            </label>
          );
        })}
      </div>

      {/* Submit Button */}
      {!showResult && (
        <div className="flex flex-col sm:flex-row justify-end gap-3">
          <button
            onClick={onSubmit}
            disabled={isSubmitDisabled()}
            className={`
              w-full sm:w-auto px-6 py-3 sm:px-8 sm:py-3 rounded-lg font-medium transition-all duration-200 touch-friendly
              ${isSubmitDisabled()
                ? 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                : 'btn-primary hover:shadow-lg active:scale-95'
              }
            `}
            aria-label="選択した回答を提出する"
          >
            <span className="flex items-center justify-center">
              回答する
              <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </span>
          </button>
        </div>
      )}
    </div>
  );
}