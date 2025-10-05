import { useState, useEffect } from 'react';
import type { Question, QuizConfig, SessionData } from '~/types';

interface QuizScreenProps {
  questions: Question[];
  config: QuizConfig;
  onComplete: (sessionData: SessionData) => void;
}

export function QuizScreen({ questions, config, onComplete }: QuizScreenProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [sessionData, setSessionData] = useState<SessionData>({
    sessionId: `session_${Date.now()}`,
    startedAt: new Date(),
    mode: config.mode,
    targetQuestionCount: config.questionCount,
    currentQuestionIndex: 0,
    answers: [],
    usedQuestionIds: [],
  });

  const currentQuestion = questions[currentQuestionIndex];
  const progress = config.mode === 'set' 
    ? ((currentQuestionIndex + 1) / config.questionCount) * 100
    : 0;

  if (!currentQuestion) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            問題が見つかりません
          </h2>
          <p className="text-gray-600">
            問題データの読み込みに失敗しました。
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* プログレスバー */}
        {config.mode === 'set' && (
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">
                問題 {currentQuestionIndex + 1} / {config.questionCount}
              </span>
              <span className="text-sm text-gray-500">
                {Math.round(progress)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* 問題表示エリア */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="mb-4">
            <div className="flex gap-2 mb-4">
              <span className="inline-block bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                {currentQuestion.domain}
              </span>
              <span className="inline-block bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded">
                {currentQuestion.difficulty}
              </span>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              {currentQuestion.question}
            </h2>
          </div>

          {/* 選択肢 */}
          <div className="space-y-3 mb-6">
            {currentQuestion.options.map((option, index) => (
              <label
                key={index}
                className="flex items-start p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <input
                  type="radio"
                  name="answer"
                  value={option.charAt(0)}
                  className="mt-1 mr-3"
                />
                <span className="text-gray-900">{option}</span>
              </label>
            ))}
          </div>

          {/* アクションボタン */}
          <div className="flex justify-between">
            <button className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors">
              スキップ
            </button>
            <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              回答する
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}