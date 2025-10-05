import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router';
import type { Route } from "./+types/quiz";
import type { Question, QuizConfig, SessionData, Answer } from '~/types';
import { QuestionLoadingSpinner, DataLoadErrorDisplay } from '~/components';

export function meta({}: Route.MetaArgs) {
  return [
    { title: "クイズ - AWS CloudOps試験対策" },
    { name: "description", content: "AWS CloudOps試験の練習問題" },
  ];
}

export default function Quiz() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [showResult, setShowResult] = useState(false);
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // URLパラメータから設定を取得
  const mode = searchParams.get('mode') as 'set' | 'endless' || 'set';
  const count = parseInt(searchParams.get('count') || '10');

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      // SimpleDataLoaderを使用してデータを読み込み
      const { loadQuestionSet } = await import('~/utils/simple-data-loader');
      const result = await loadQuestionSet();
      
      if (!result.success || !result.data) {
        throw new Error(result.error || '問題データの読み込みに失敗しました');
      }

      setQuestions(result.data.questions);
      
      // セッションデータを初期化
      const session: SessionData = {
        sessionId: `session_${Date.now()}`,
        startedAt: new Date(),
        mode,
        targetQuestionCount: mode === 'set' ? count : undefined,
        currentQuestionIndex: 0,
        answers: [],
        usedQuestionIds: [],
      };
      setSessionData(session);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : '不明なエラーが発生しました');
      setLoading(false);
    }
  };

  const handleAnswerSelect = (answer: string) => {
    setSelectedAnswer(answer);
  };

  const handleSubmitAnswer = () => {
    if (!selectedAnswer || !sessionData) return;

    const currentQuestion = questions[currentQuestionIndex];
    const isCorrect = selectedAnswer === currentQuestion.correctAnswer;
    
    const newAnswer: Answer = {
      questionId: currentQuestion.id,
      userAnswer: selectedAnswer,
      correctAnswer: currentQuestion.correctAnswer,
      isCorrect,
      answeredAt: new Date(),
    };

    const updatedSession = {
      ...sessionData,
      answers: [...sessionData.answers, newAnswer],
      usedQuestionIds: [...sessionData.usedQuestionIds, currentQuestion.id],
    };

    setSessionData(updatedSession);
    setShowResult(true);
  };

  const handleNextQuestion = () => {
    if (mode === 'set' && currentQuestionIndex + 1 >= count) {
      // 10問セット完了
      navigate('/result', { state: { sessionData } });
      return;
    }

    // 次の問題へ
    setCurrentQuestionIndex(prev => prev + 1);
    setSelectedAnswer('');
    setShowResult(false);
  };

  if (loading) {
    return <QuestionLoadingSpinner />;
  }

  if (error) {
    return (
      <DataLoadErrorDisplay 
        onRetry={() => {
          setError(null);
          setLoading(true);
          loadQuestions();
        }}
      />
    );
  }

  if (currentQuestionIndex >= questions.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            すべての問題が完了しました
          </h2>
          <button
            onClick={() => navigate('/result', { state: { sessionData } })}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            結果を見る
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = mode === 'set' ? ((currentQuestionIndex + 1) / count) * 100 : 0;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* プログレスバー */}
        {mode === 'set' && (
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">
                問題 {currentQuestionIndex + 1} / {count}
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
                className={`flex items-start p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedAnswer === option.charAt(0)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:bg-gray-50'
                } ${showResult ? 'pointer-events-none' : ''}`}
              >
                <input
                  type="radio"
                  name="answer"
                  value={option.charAt(0)}
                  checked={selectedAnswer === option.charAt(0)}
                  onChange={(e) => handleAnswerSelect(e.target.value)}
                  disabled={showResult}
                  className="mt-1 mr-3"
                />
                <span className="text-gray-900">{option}</span>
              </label>
            ))}
          </div>

          {/* 結果表示 */}
          {showResult && (
            <div className="mb-6 p-4 rounded-lg bg-gray-50">
              <div className={`text-lg font-semibold mb-2 ${
                selectedAnswer === currentQuestion.correctAnswer ? 'text-green-600' : 'text-red-600'
              }`}>
                {selectedAnswer === currentQuestion.correctAnswer ? '正解！' : '不正解'}
              </div>
              <p className="text-gray-700 mb-2">
                正解: {currentQuestion.correctAnswer}
              </p>
              <div className="text-gray-700">
                <h4 className="font-medium mb-2">解説:</h4>
                <p>{currentQuestion.explanation}</p>
              </div>
              {currentQuestion.learningResources.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium mb-2">学習リソース:</h4>
                  <ul className="space-y-1">
                    {currentQuestion.learningResources.map((resource, index) => (
                      <li key={index}>
                        <a
                          href={resource.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 underline"
                        >
                          {resource.title}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* アクションボタン */}
          <div className="flex justify-between">
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              メニューに戻る
            </button>
            {!showResult ? (
              <button
                onClick={handleSubmitAnswer}
                disabled={!selectedAnswer}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                回答する
              </button>
            ) : (
              <button
                onClick={handleNextQuestion}
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
              >
                {mode === 'set' && currentQuestionIndex + 1 >= count ? '結果を見る' : '次の問題'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}