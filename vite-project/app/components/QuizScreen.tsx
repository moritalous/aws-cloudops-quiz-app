import { useState, useEffect } from 'react';
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

  const currentQuestion = questions[currentQuestionIndex];

  // Reset selected answer when question changes
  useEffect(() => {
    if (currentQuestion) {
      setSelectedAnswer(currentQuestion.type === 'multiple' ? [] : '');
    }
  }, [currentQuestionIndex, currentQuestion]);
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

        {/* エンドレスモード用の問題カウンター */}
        {config.mode === 'endless' && (
          <div className="mb-6">
            <div className="text-center">
              <span className="text-lg font-medium text-gray-700">
                問題 {currentQuestionIndex + 1}
              </span>
              <span className="text-sm text-gray-500 ml-2">
                (エンドレスモード)
              </span>
            </div>
          </div>
        )}

        {/* 問題表示 */}
        <QuestionDisplay
          question={currentQuestion}
          selectedAnswer={selectedAnswer}
          onAnswerSelect={setSelectedAnswer}
          onSubmit={handleSubmitAnswer}
          showResult={showResult}
        />

        {/* 結果表示 */}
        {showResult && getCurrentAnswer() && (
          <ResultDisplay
            question={currentQuestion}
            answer={getCurrentAnswer()!}
            onNext={handleNextQuestion}
          />
        )}
      </div>
    </div>
  );
}