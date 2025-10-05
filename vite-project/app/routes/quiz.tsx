import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router';
import type { Route } from './+types/quiz';
import type { Question, QuizConfig, SessionData } from '~/types';
import { QuizScreen } from '~/components/QuizScreen';
import { QuestionLoadingSpinner, DataLoadErrorDisplay } from '~/components';
import { loadQuestionSet } from '~/utils/simple-data-loader';

export function meta({}: Route.MetaArgs) {
  return [
    { title: 'クイズ - AWS CloudOps試験対策' },
    { name: 'description', content: 'AWS CloudOps試験の練習問題' },
  ];
}

export default function Quiz() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // URLパラメータから設定を取得
  const mode = (searchParams.get('mode') as 'set' | 'endless') || 'set';
  const count = parseInt(searchParams.get('count') || '10');
  const domainFilter = searchParams.get('domain') || undefined;

  const config: QuizConfig = {
    mode,
    questionCount: count,
    domain: domainFilter,
  };

  useEffect(() => {
    initializeQuiz();
  }, []);

  const initializeQuiz = async () => {
    try {
      const result = await loadQuestionSet();

      if (!result.success || !result.data) {
        throw new Error(result.error || '問題データの読み込みに失敗しました');
      }

      let questionsToUse = result.data.questions;

      // ドメインフィルターが指定されている場合
      if (domainFilter) {
        questionsToUse = questionsToUse.filter(
          (q) => q.domain === domainFilter
        );
      }

      setQuestions(questionsToUse);
      setLoading(false);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : '不明なエラーが発生しました'
      );
      setLoading(false);
    }
  };

  const handleQuizComplete = (sessionData: SessionData) => {
    navigate('/result', { state: { session: sessionData } });
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
          initializeQuiz();
        }}
      />
    );
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            問題が見つかりません
          </h2>
          <p className="text-gray-600 mb-4">
            指定されたドメインの問題データが見つかりませんでした。
          </p>
          <button
            onClick={() => navigate('/')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            メニューに戻る
          </button>
        </div>
      </div>
    );
  }

  return (
    <QuizScreen
      questions={questions}
      config={config}
      onComplete={handleQuizComplete}
    />
  );
}
