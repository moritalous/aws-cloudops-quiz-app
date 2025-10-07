import type { Route } from './+types/home';
import { Link } from 'react-router';

export function meta({}: Route.MetaArgs) {
  return [
    { title: 'AWS CloudOps試験対策' },
    {
      name: 'description',
      content:
        'AWS Certified CloudOps Engineer - Associate試験対策アプリケーション',
    },
  ];
}

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900">
      <div className="container-responsive py-6 sm:py-8 md:py-12">
        {/* ヘッダー */}
        <header className="text-center mb-8 sm:mb-12">
          <h1 className="text-responsive-3xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
            AWS CloudOps 試験対策
          </h1>
          <p className="text-responsive-lg text-gray-700 dark:text-gray-300 mb-2">
            AWS Certified CloudOps Engineer - Associate
          </p>
          <p className="text-responsive-base text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            実践的な問題で試験準備を効率的に進めましょう
          </p>
        </header>

        {/* 学習モード選択 */}
        <section className="mb-8 sm:mb-12" aria-labelledby="learning-modes">
          <h2 id="learning-modes" className="sr-only">
            学習モード選択
          </h2>
          <div className="grid-responsive-2 gap-4 sm:gap-6">
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
                <Link
                  to="/quiz?mode=set&count=10"
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
                </Link>
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
                <Link
                  to="/quiz?mode=endless"
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
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* ドメイン別学習 */}
        <section
          className="card-base mb-8 sm:mb-12"
          aria-labelledby="domain-learning"
        >
          <h3
            id="domain-learning"
            className="text-responsive-lg font-semibold text-gray-900 dark:text-white mb-4 sm:mb-6"
          >
            ドメイン別学習
          </h3>
          <p className="text-responsive-sm text-gray-600 dark:text-gray-300 mb-4 sm:mb-6">
            特定のドメインに集中して学習したい場合は、以下から選択してください。
          </p>
          <div className="grid-responsive-3 gap-3 sm:gap-4">
            <Link
              to="/quiz?mode=set&count=10&domain=monitoring"
              className="flex items-center p-3 sm:p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-l-4 border-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
            >
              <div className="flex-grow">
                <h4 className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">
                  監視・ロギング
                </h4>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                  20% - CloudWatch, CloudTrail
                </p>
              </div>
              <div className="text-right">
                <span className="text-lg sm:text-xl font-bold text-blue-600 dark:text-blue-400">
                  20%
                </span>
              </div>
            </Link>

            <Link
              to="/quiz?mode=set&count=10&domain=reliability"
              className="flex items-center p-3 sm:p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border-l-4 border-green-500 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
            >
              <div className="flex-grow">
                <h4 className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">
                  信頼性・継続性
                </h4>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                  32% - Auto Scaling, ELB
                </p>
              </div>
              <div className="text-right">
                <span className="text-lg sm:text-xl font-bold text-green-600 dark:text-green-400">
                  32%
                </span>
              </div>
            </Link>

            <Link
              to="/quiz?mode=set&count=10&domain=deployment"
              className="flex items-center p-3 sm:p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border-l-4 border-yellow-500 hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-colors"
            >
              <div className="flex-grow">
                <h4 className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">
                  デプロイメント
                </h4>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                  20% - CodeDeploy, CloudFormation
                </p>
              </div>
              <div className="text-right">
                <span className="text-lg sm:text-xl font-bold text-yellow-600 dark:text-yellow-400">
                  20%
                </span>
              </div>
            </Link>

            <Link
              to="/quiz?mode=set&count=10&domain=security"
              className="flex items-center p-3 sm:p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border-l-4 border-red-500 hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
            >
              <div className="flex-grow">
                <h4 className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">
                  セキュリティ
                </h4>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                  16% - IAM, GuardDuty
                </p>
              </div>
              <div className="text-right">
                <span className="text-lg sm:text-xl font-bold text-red-600 dark:text-red-400">
                  16%
                </span>
              </div>
            </Link>

            <Link
              to="/quiz?mode=set&count=10&domain=networking"
              className="flex items-center p-3 sm:p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border-l-4 border-purple-500 hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
            >
              <div className="flex-grow">
                <h4 className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">
                  ネットワーク
                </h4>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                  12% - VPC, Route Tables
                </p>
              </div>
              <div className="text-right">
                <span className="text-lg sm:text-xl font-bold text-purple-600 dark:text-purple-400">
                  12%
                </span>
              </div>
            </Link>
          </div>
        </section>

        {/* 試験情報 */}
        <section className="card-base" aria-labelledby="exam-info">
          <h3
            id="exam-info"
            className="text-responsive-lg font-semibold text-gray-900 dark:text-white mb-4 sm:mb-6"
          >
            試験について
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 dark:text-white mb-3 text-responsive-sm flex items-center">
                <svg
                  className="w-4 h-4 mr-2 text-blue-600 dark:text-blue-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                試験形式
              </h4>
              <ul className="text-responsive-xs text-gray-600 dark:text-gray-300 space-y-2">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 flex-shrink-0"></span>
                  選択問題（単一回答・複数回答）
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 flex-shrink-0"></span>
                  試験時間: 180分
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 flex-shrink-0"></span>
                  問題数: 65問
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 flex-shrink-0"></span>
                  合格点: 720/1000点
                </li>
              </ul>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 dark:text-white mb-3 text-responsive-sm flex items-center">
                <svg
                  className="w-4 h-4 mr-2 text-green-600 dark:text-green-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
                学習のコツ
              </h4>
              <ul className="text-responsive-xs text-gray-600 dark:text-gray-300 space-y-2">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2 flex-shrink-0"></span>
                  各ドメインをバランスよく学習
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2 flex-shrink-0"></span>
                  実際のAWSサービスを触って理解
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2 flex-shrink-0"></span>
                  間違えた問題は解説をしっかり読む
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2 flex-shrink-0"></span>
                  定期的に復習を行う
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* フッター */}
        <footer className="mt-8 sm:mt-12 text-center">
          <p className="text-responsive-xs text-gray-500 dark:text-gray-400">
            問題は生成AIで作成しました。正しいかわかりません
          </p>
        </footer>
      </div>
    </div>
  );
}
