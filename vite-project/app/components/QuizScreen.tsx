import { useState, useEffect, useRef } from 'react';
import type { Question, QuizConfig, SessionData, Answer } from '~/types';
import { QuestionDisplay } from './QuestionDisplay';
import { ResultDisplay } from './ResultDisplay';

interface QuizScreenProps {
  questions: Question[];
  config: QuizConfig;
  onComplete: (sessionData: SessionData) => void;
}

export function QuizScreen({ questions, config, onComplete }: QuizScreenProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | string[]>('');
  const [showResult, setShowResult] = useState(false);
  const [sessionData, setSessionData] = useState<SessionData>({
    sessionId: `session_${Date.now()}`,
    startedAt: new Date(),
    mode: config.mode,
    targetQuestionCount: config.questionCount,
    currentQuestionIndex: 0,
    answers: [],
    usedQuestionIds: [],
  });

  // Touch gesture handling
  const touchStartX = useRef<number>(0);
  const touchStartY = useRef<number>(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const currentQuestion = questions[currentQuestionIndex];

  // Reset selected answer when question changes
  useEffect(() => {
    if (currentQuestion) {
      setSelectedAnswer(currentQuestion.type === 'multiple' ? [] : '');
    }
  }, [currentQuestionIndex, currentQuestion]);

  // Touch gesture handlers
  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
    touchStartY.current = e.touches[0].clientY;
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (!e.changedTouches[0]) return;

    const touchEndX = e.changedTouches[0].clientX;
    const touchEndY = e.changedTouches[0].clientY;
    const deltaX = touchEndX - touchStartX.current;
    const deltaY = touchEndY - touchStartY.current;

    // Only process horizontal swipes (ignore vertical scrolling)
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
      // Swipe right - go to previous question (if available)
      if (deltaX > 0 && currentQuestionIndex > 0 && !showResult) {
        const prevIndex = currentQuestionIndex - 1;
        setCurrentQuestionIndex(prevIndex);
        setShowResult(false);
      }
      // Swipe left - go to next question (if result is shown)
      else if (deltaX < 0 && showResult) {
        handleNextQuestion();
      }
    }
  };
  const progress = config.mode === 'set' 
    ? ((currentQuestionIndex + 1) / config.questionCount) * 100
    : 0;

  const handleSubmitAnswer = () => {
    if (!currentQuestion) return;

    const correctAnswer = currentQuestion.correctAnswer;
    let isCorrect = false;

    // Check if answer is correct
    if (currentQuestion.type === 'single') {
      isCorrect = selectedAnswer === correctAnswer;
    } else {
      // For multiple choice, compare arrays
      const userAnswers = Array.isArray(selectedAnswer) ? selectedAnswer.sort() : [selectedAnswer].sort();
      const correctAnswers = Array.isArray(correctAnswer) ? correctAnswer.sort() : [correctAnswer].sort();
      isCorrect = JSON.stringify(userAnswers) === JSON.stringify(correctAnswers);
    }

    const newAnswer: Answer = {
      questionId: currentQuestion.id,
      userAnswer: selectedAnswer,
      correctAnswer: correctAnswer,
      isCorrect,
      answeredAt: new Date()
    };

    const updatedSessionData = {
      ...sessionData,
      answers: [...sessionData.answers, newAnswer],
      usedQuestionIds: [...sessionData.usedQuestionIds, currentQuestion.id],
      currentQuestionIndex: currentQuestionIndex
    };

    setSessionData(updatedSessionData);
    setShowResult(true);
  };

  const handleNextQuestion = () => {
    const nextIndex = currentQuestionIndex + 1;
    
    // Check if quiz is complete
    if (config.mode === 'set' && nextIndex >= config.questionCount) {
      onComplete(sessionData);
      return;
    }
    
    if (nextIndex >= questions.length) {
      onComplete(sessionData);
      return;
    }

    // Move to next question
    setCurrentQuestionIndex(nextIndex);
    const nextQuestion = questions[nextIndex];
    setSelectedAnswer(nextQuestion?.type === 'multiple' ? [] : '');
    setShowResult(false);
  };

  const getCurrentAnswer = (): Answer | undefined => {
    return sessionData.answers[sessionData.answers.length - 1];
  };

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
    <div 
      className="min-h-screen bg-gray-50 dark:bg-gray-900 py-4 sm:py-6 md:py-8"
      ref={containerRef}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      <div className="container-responsive">
        {/* ヘッダー */}
        <header className="mb-4 sm:mb-6">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => window.history.back()}
              className="btn-secondary text-sm sm:text-base"
              aria-label="メニューに戻る"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="hidden sm:inline">メニューに戻る</span>
              <span className="sm:hidden">戻る</span>
            </button>
            
            <div className="text-center">
              <h1 className="text-responsive-lg font-semibold text-gray-900 dark:text-white">
                {config.mode === 'set' ? '10問セット' : 'エンドレスモード'}
              </h1>
            </div>
            
            <div className="w-20 sm:w-24"></div> {/* Spacer for centering */}
          </div>

          {/* プログレスバー - 10問セットモード */}
          {config.mode === 'set' && (
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3 sm:p-4 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex justify-between items-center mb-2 sm:mb-3">
                <span className="text-responsive-sm font-medium text-gray-700 dark:text-gray-300">
                  問題 {currentQuestionIndex + 1} / {config.questionCount}
                </span>
                <span className="text-responsive-sm text-gray-500 dark:text-gray-400 font-mono">
                  {Math.round(progress)}%
                </span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                  role="progressbar"
                  aria-valuenow={progress}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`進捗: ${Math.round(progress)}%`}
                />
              </div>
            </div>
          )}

          {/* エンドレスモード用の統計表示 */}
          {config.mode === 'endless' && (
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3 sm:p-4 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div className="text-responsive-lg font-bold text-blue-600 dark:text-blue-400">
                    {currentQuestionIndex + 1}
                  </div>
                  <div className="text-responsive-xs text-gray-500 dark:text-gray-400">
                    問題数
                  </div>
                </div>
                <div>
                  <div className="text-responsive-lg font-bold text-green-600 dark:text-green-400">
                    {sessionData.answers.length > 0 
                      ? Math.round((sessionData.answers.filter(a => a.isCorrect).length / sessionData.answers.length) * 100)
                      : 0}%
                  </div>
                  <div className="text-responsive-xs text-gray-500 dark:text-gray-400">
                    正答率
                  </div>
                </div>
              </div>
            </div>
          )}
        </header>

        {/* 問題表示 */}
        <main className="mb-6">
          <QuestionDisplay
            question={currentQuestion}
            selectedAnswer={selectedAnswer}
            onAnswerSelect={setSelectedAnswer}
            onSubmit={handleSubmitAnswer}
            showResult={showResult}
          />
        </main>

        {/* 結果表示 */}
        {showResult && getCurrentAnswer() && (
          <section aria-live="polite" aria-label="問題の結果">
            <ResultDisplay
              question={currentQuestion}
              answer={getCurrentAnswer()!}
              onNext={handleNextQuestion}
            />
          </section>
        )}

        {/* スワイプヒント（モバイルのみ） */}
        <div className="block sm:hidden mt-4 text-center">
          <div className="inline-flex items-center text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded-full">
            {showResult ? (
              <>
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                左にスワイプで次の問題
              </>
            ) : currentQuestionIndex > 0 ? (
              <>
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                右にスワイプで前の問題
              </>
            ) : (
              <span>回答後、左にスワイプで次の問題</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}