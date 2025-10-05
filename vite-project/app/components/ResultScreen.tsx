import { Link } from 'react-router';
import type { SessionData, QuizStatistics } from '~/types';

interface ResultScreenProps {
  sessionData: SessionData;
  statistics: QuizStatistics;
  onRestart: () => void;
}

export function ResultScreen({ sessionData, statistics, onRestart }: ResultScreenProps) {
  const getScoreColor = (accuracy: number) => {
    if (accuracy >= 80) return 'text-green-600';
    if (accuracy >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (accuracy: number) => {
    if (accuracy >= 80) return 'bg-green-100';
    if (accuracy >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            クイズ結果
          </h1>
          <p className="text-gray-600">
            お疲れさまでした！結果を確認しましょう。
          </p>
        </div>

        {/* 総合スコア */}
        <div className={`${getScoreBgColor(statistics.accuracy)} rounded-lg p-6 mb-6`}>
          <div className="text-center">
            <div className={`text-6xl font-bold ${getScoreColor(statistics.accuracy)} mb-2`}>
              {Math.round(statistics.accuracy)}%
            </div>
            <p className="text-lg text-gray-700">
              {statistics.correctAnswers} / {statistics.totalQuestions} 問正解
            </p>
          </div>
        </div>

        {/* ドメイン別結果 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            ドメイン別成績
          </h2>
          <div className="space-y-4">
            {Object.entries(statistics.domainBreakdown).map(([domain, stats]) => (
              <div key={domain} className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-medium text-gray-900 capitalize">
                      {domain}
                    </span>
                    <span className="text-sm text-gray-600">
                      {stats.correct} / {stats.total}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${stats.accuracy}%` }}
                    />
                  </div>
                </div>
                <div className="ml-4 text-right">
                  <span className={`font-semibold ${getScoreColor(stats.accuracy)}`}>
                    {Math.round(stats.accuracy)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* セッション情報 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            セッション情報
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <span className="text-gray-600">学習モード:</span>
              <span className="ml-2 font-medium">
                {sessionData.mode === 'set' ? '10問セット' : 'エンドレス'}
              </span>
            </div>
            <div>
              <span className="text-gray-600">開始時刻:</span>
              <span className="ml-2 font-medium">
                {sessionData.startedAt.toLocaleString('ja-JP')}
              </span>
            </div>
            {statistics.averageTimePerQuestion && (
              <div>
                <span className="text-gray-600">平均回答時間:</span>
                <span className="ml-2 font-medium">
                  {Math.round(statistics.averageTimePerQuestion)}秒
                </span>
              </div>
            )}
          </div>
        </div>

        {/* アクションボタン */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={onRestart}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            もう一度挑戦
          </button>
          <Link
            to="/"
            className="bg-gray-600 text-white px-8 py-3 rounded-lg hover:bg-gray-700 transition-colors font-medium text-center"
          >
            メニューに戻る
          </Link>
        </div>
      </div>
    </div>
  );
}