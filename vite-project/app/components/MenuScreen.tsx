import { Link } from 'react-router';
import type { QuizConfig } from '~/types';

interface MenuScreenProps {
  onStart: (config: QuizConfig) => void;
}

export function MenuScreen({ onStart }: MenuScreenProps) {
  const handleStartSet = () => {
    onStart({
      mode: 'set',
      questionCount: 10,
    });
  };

  const handleStartEndless = () => {
    onStart({
      mode: 'endless',
      questionCount: 0,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 md:py-12">
        {/* ヘッダー */}
        <header className="text-center mb-8 sm:mb-12">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
            AWS CloudOps 試験対策
          </h1>
          <p className="text-lg sm:text-xl md:text-2xl text-gray-700 dark:text-gray-300 mb-2">
            AWS Certified CloudOps Engineer - Associate
          </p>
          <p className="text-base sm:text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            実践的な問題で試験準備を効率的に進めましょう
          </p>
        </header>

        {/* 学習モード選択 */}
        <section className="mb-8 sm:mb-12" aria-labelledby="learning-modes">
          <h2 id="learning-modes" className="sr-only">
            学習モード選択
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
            <div className="card-interactive group">
              <div className="flex flex-col h-full">
                <div className="flex items-center mb-3 sm:mb-4">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mr-3">
                    <svg
                      className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600 dark:text-blue-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                      />
                    </svg>
                  </div>
                  <h3 className="text-responsive-lg font-semibold text-gray-900 dark:text-white">
                    10問セット
                  </h3>
                </div>
                <p className="text-responsive-sm text-gray-600 dark:text-gray-300 mb-6 flex-grow leading-relaxed">
                  10問の問題に挑戦して、正答率を確認できます。短時間で集中して学習したい方におすすめです。
                </p>
                <button
                  onClick={handleStartSet}
                  className="btn-primary w-full group-hover:scale-105 transition-transform"
                  aria-label="10問セットモードを開始"
                >
                  <span>10問セットを開始</span>
                  <svg
                    className="w-4 h-4 ml-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <div className="card-interactive group">
              <div className="flex flex-col h-full">
                <div className="flex items-center mb-3 sm:mb-4">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center mr-3">
                    <svg
                      className="w-5 h-5 sm:w-6 sm:h-6 text-green-600 dark:text-green-400"
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
                  </div>
                  <h3 className="text-responsive-lg font-semibold text-gray-900 dark:text-white">
                    エンドレスモード
                  </h3>
                </div>
                <p className="text-responsive-sm text-gray-600 dark:text-gray-300 mb-6 flex-grow leading-relaxed">
                  時間制限なしで連続して問題に取り組めます。じっくりと学習を進めたい方におすすめです。
                </p>
                <button
                  onClick={handleStartEndless}
                  className="btn-success w-full group-hover:scale-105 transition-transform"
                  aria-label="エンドレスモードを開始"
                >
                  <span>エンドレスモードを開始</span>
                  <svg
                    className="w-4 h-4 ml-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* 試験ドメイン情報 */}
        <section className="card-base" aria-labelledby="exam-domains">
          <h3
            id="exam-domains"
            className="text-responsive-lg font-semibold text-gray-900 dark:text-white mb-4 sm:mb-6"
          >
            試験ドメイン
          </h3>
          <div className="grid-responsive-3 gap-3 sm:gap-4">
            <div className="flex items-center p-3 sm:p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-l-4 border-blue-500">
              <div className="flex-grow">
                <h4 className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">
                  監視・ロギング
                </h4>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                  Monitoring & Logging
                </p>
              </div>
              <div className="text-right">
                <span className="text-lg sm:text-xl font-bold text-blue-600 dark:text-blue-400">
                  20%
                </span>
              </div>
            </div>

            <div className="flex items-center p-3 sm:p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border-l-4 border-green-500">
              <div className="flex-grow">
                <h4 className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">
                  信頼性・継続性
                </h4>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                  Reliability & Business Continuity
                </p>
              </div>
              <div className="text-right">
                <span className="text-lg sm:text-xl font-bold text-green-600 dark:text-green-400">
                  32%
                </span>
              </div>
            </div>

            <div className="flex items-center p-3 sm:p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border-l-4 border-yellow-500">
              <div className="flex-grow">
                <h4 className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">
                  デプロイメント
                </h4>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                  Deployment & Provisioning
                </p>
              </div>
              <div className="text-right">
                <span className="text-lg sm:text-xl font-bold text-yellow-600 dark:text-yellow-400">
                  20%
                </span>
              </div>
            </div>

            <div className="flex items-center p-3 sm:p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border-l-4 border-red-500">
              <div className="flex-grow">
                <h4 className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">
                  セキュリティ
                </h4>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                  Security & Compliance
                </p>
              </div>
              <div className="text-right">
                <span className="text-lg sm:text-xl font-bold text-red-600 dark:text-red-400">
                  16%
                </span>
              </div>
            </div>

            <div className="flex items-center p-3 sm:p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border-l-4 border-purple-500">
              <div className="flex-grow">
                <h4 className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">
                  ネットワーク
                </h4>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                  Networking & Content Delivery
                </p>
              </div>
              <div className="text-right">
                <span className="text-lg sm:text-xl font-bold text-purple-600 dark:text-purple-400">
                  12%
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* フッター情報 */}
        <footer className="mt-8 sm:mt-12 text-center">
          <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
            © 2025 AWS CloudOps 試験対策アプリ
          </p>
        </footer>
      </div>
    </div>
  );
}
