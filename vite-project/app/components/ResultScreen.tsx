import { Link } from 'react-router';
import type { SessionData, QuizStatistics } from '~/types';

interface ResultScreenProps {
  sessionData: SessionData;
  statistics: QuizStatistics;
  onRestart: () => void;
}

export function ResultScreen({
  sessionData,
  statistics,
  onRestart,
}: ResultScreenProps) {
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-4 sm:py-6 md:py-8">
      <div className="container-responsive">
        {/* Header */}
        <header className="text-center mb-6 sm:mb-8">
          <h1 className="text-responsive-2xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
            クイズ結果
          </h1>
          <p className="text-responsive-base text-gray-600 dark:text-gray-400">
            お疲れさまでした！結果を確認しましょう。
          </p>
        </header>

        {/* Overall Score */}
        <div
          className={`${getScoreBgColor(statistics.accuracy)} dark:bg-opacity-20 rounded-lg p-4 sm:p-6 mb-4 sm:mb-6 border`}
        >
          <div className="text-center">
            <div className="flex items-center justify-center mb-3 sm:mb-4">
              {statistics.accuracy >= 80 ? (
                <svg
                  className="w-8 h-8 sm:w-12 sm:h-12 text-green-600 dark:text-green-400 mr-2 sm:mr-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              ) : statistics.accuracy >= 60 ? (
                <svg
                  className="w-8 h-8 sm:w-12 sm:h-12 text-yellow-600 dark:text-yellow-400 mr-2 sm:mr-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              ) : (
                <svg
                  className="w-8 h-8 sm:w-12 sm:h-12 text-red-600 dark:text-red-400 mr-2 sm:mr-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              )}
              <div>
                <div
                  className={`text-4xl sm:text-5xl md:text-6xl font-bold ${getScoreColor(statistics.accuracy)} mb-1 sm:mb-2`}
                >
                  {Math.round(statistics.accuracy)}%
                </div>
                <p className="text-responsive-base text-gray-700 dark:text-gray-300">
                  {statistics.correctAnswers} / {statistics.totalQuestions}{' '}
                  問正解
                </p>
              </div>
            </div>

            {/* Performance Message */}
            <div className="mt-3 sm:mt-4">
              {statistics.accuracy >= 80 ? (
                <p className="text-green-700 dark:text-green-300 font-medium text-responsive-sm">
                  🎉 素晴らしい成績です！
                </p>
              ) : statistics.accuracy >= 60 ? (
                <p className="text-yellow-700 dark:text-yellow-300 font-medium text-responsive-sm">
                  👍 良い成績です！もう少し頑張りましょう。
                </p>
              ) : (
                <p className="text-red-700 dark:text-red-300 font-medium text-responsive-sm">
                  💪 復習して再挑戦しましょう！
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Domain Breakdown */}
        <div className="card-base mb-4 sm:mb-6">
          <h2 className="text-responsive-lg font-semibold text-gray-900 dark:text-white mb-4 sm:mb-6">
            ドメイン別成績
          </h2>
          <div className="space-y-3 sm:space-y-4">
            {Object.entries(statistics.domainBreakdown).map(
              ([domain, stats]) => (
                <div
                  key={domain}
                  className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 sm:p-4"
                >
                  <div className="flex items-center justify-between mb-2 sm:mb-3">
                    <div className="flex-1">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-1 sm:mb-2">
                        <span className="font-medium text-gray-900 dark:text-white capitalize text-responsive-sm">
                          {domain}
                        </span>
                        <span className="text-responsive-xs text-gray-600 dark:text-gray-400">
                          {stats.correct} / {stats.total} 問
                        </span>
                      </div>
                      <div className="progress-bar">
                        <div
                          className={`progress-fill ${
                            stats.accuracy >= 80
                              ? 'bg-green-600'
                              : stats.accuracy >= 60
                                ? 'bg-yellow-600'
                                : 'bg-red-600'
                          }`}
                          style={{ width: `${stats.accuracy}%` }}
                          role="progressbar"
                          aria-valuenow={stats.accuracy}
                          aria-valuemin={0}
                          aria-valuemax={100}
                          aria-label={`${domain}の正答率: ${Math.round(stats.accuracy)}%`}
                        />
                      </div>
                    </div>
                    <div className="ml-3 sm:ml-4 text-right">
                      <span
                        className={`font-bold text-responsive-sm ${getScoreColor(stats.accuracy)}`}
                      >
                        {Math.round(stats.accuracy)}%
                      </span>
                    </div>
                  </div>
                </div>
              )
            )}
          </div>
        </div>

        {/* Session Information */}
        <div className="card-base mb-6 sm:mb-8">
          <h2 className="text-responsive-lg font-semibold text-gray-900 dark:text-white mb-4 sm:mb-6">
            セッション情報
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <svg
                className="w-5 h-5 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                />
              </svg>
              <div>
                <span className="text-responsive-xs text-gray-600 dark:text-gray-400 block">
                  学習モード
                </span>
                <span className="font-medium text-gray-900 dark:text-white text-responsive-sm">
                  {sessionData.mode === 'set' ? '10問セット' : 'エンドレス'}
                </span>
              </div>
            </div>

            <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <svg
                className="w-5 h-5 text-green-600 dark:text-green-400 mr-3 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div>
                <span className="text-responsive-xs text-gray-600 dark:text-gray-400 block">
                  開始時刻
                </span>
                <span className="font-medium text-gray-900 dark:text-white text-responsive-sm">
                  {sessionData.startedAt.toLocaleString('ja-JP', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
            </div>

            {statistics.averageTimePerQuestion && (
              <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg sm:col-span-2">
                <svg
                  className="w-5 h-5 text-purple-600 dark:text-purple-400 mr-3 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
                <div>
                  <span className="text-responsive-xs text-gray-600 dark:text-gray-400 block">
                    平均回答時間
                  </span>
                  <span className="font-medium text-gray-900 dark:text-white text-responsive-sm">
                    {Math.round(statistics.averageTimePerQuestion)}秒
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
          <button
            onClick={onRestart}
            className="btn-primary w-full sm:w-auto px-6 sm:px-8 py-3 hover:shadow-lg active:scale-95"
            aria-label="同じモードでもう一度挑戦する"
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            もう一度挑戦
          </button>
          <Link
            to="/"
            className="btn-secondary w-full sm:w-auto px-6 sm:px-8 py-3 text-center hover:shadow-lg active:scale-95"
            aria-label="メニュー画面に戻る"
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
              />
            </svg>
            メニューに戻る
          </Link>
        </div>

        {/* Footer */}
        <footer className="mt-8 sm:mt-12 text-center">
          <p className="text-responsive-xs text-gray-500 dark:text-gray-400">
            学習を継続して、AWS CloudOps
            Engineer認定試験の合格を目指しましょう！
          </p>
        </footer>
      </div>
    </div>
  );
}
