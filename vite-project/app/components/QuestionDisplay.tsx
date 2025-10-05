import { useState } from 'react';
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
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Question Header */}
      <div className="mb-6">
        <div className="flex gap-2 mb-4">
          <span className="inline-block bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
            {question.domain}
          </span>
          <span className="inline-block bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded">
            {question.difficulty}
          </span>
          <span className="inline-block bg-purple-100 text-purple-800 text-xs font-medium px-2.5 py-0.5 rounded">
            {question.type === 'single' ? '単一回答' : '複数回答'}
          </span>
        </div>
        
        <h2 className="text-xl font-semibold text-gray-900 leading-relaxed">
          {question.question}
        </h2>
        
        {question.type === 'multiple' && (
          <p className="text-sm text-gray-600 mt-2">
            ※ 複数の選択肢を選択してください
          </p>
        )}
      </div>

      {/* Options */}
      <div className="space-y-3 mb-6">
        {question.options.map((option, index) => {
          const optionValue = getOptionLetter(option);
          const isSelected = isAnswerSelected(optionValue);
          
          return (
            <label
              key={index}
              className={`
                flex items-start p-4 border rounded-lg cursor-pointer transition-all duration-200
                ${isSelected 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 hover:bg-gray-50'
                }
                ${(disabled || showResult) ? 'cursor-not-allowed opacity-60' : ''}
              `}
            >
              <input
                type={question.type === 'single' ? 'radio' : 'checkbox'}
                name={question.type === 'single' ? `question-${question.id}` : `answer-${question.id}`}
                value={optionValue}
                checked={isSelected}
                onChange={(e) => {
                  if (question.type === 'single') {
                    handleSingleAnswerSelect(optionValue);
                  } else {
                    handleMultipleAnswerSelect(optionValue);
                  }
                }}
                disabled={disabled || showResult}
                className="mt-1 mr-3 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-gray-900 leading-relaxed">
                {option}
              </span>
            </label>
          );
        })}
      </div>

      {/* Submit Button */}
      {!showResult && (
        <div className="flex justify-end">
          <button
            onClick={onSubmit}
            disabled={isSubmitDisabled()}
            className={`
              px-6 py-3 rounded-lg font-medium transition-colors
              ${isSubmitDisabled()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
              }
            `}
          >
            回答する
          </button>
        </div>
      )}
    </div>
  );
}