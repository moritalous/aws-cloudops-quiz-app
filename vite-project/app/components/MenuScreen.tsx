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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* ヘッダー */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AWS CloudOps 試験対策
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            AWS Certified CloudOps Engineer - Associate
          </p>
          <p className="text-gray-500">
            実践的な問題で試験準備を効率的に進めましょう
          </p>
        </div>

        {/* 学習モード選択 */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              10問セット
            </h2>
            <p className="text-gray-600 mb-6">
              10問の問題に挑戦して、正答率を確認できます。短時間で集中して学習したい方におすすめです。
            </p>
            <button
              onClick={handleStartSet}
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              10問セットを開始
            </button>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              エンドレスモード
            </h2>
            <p className="text-gray-600 mb-6">
              時間制限なしで連続して問題に取り組めます。じっくりと学習を進めたい方におすすめです。
            </p>
            <button
              onClick={handleStartEndless}
              className="inline-block bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              エンドレスモードを開始
            </button>
          </div>
        </div>

        {/* 試験ドメイン情報 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            試験ドメイン
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="border-l-4 border-blue-500 pl-4">
              <h4 className="font-medium text-gray-900">監視・ロギング</h4>
              <p className="text-sm text-gray-600">20%</p>
            </div>
            <div className="border-l-4 border-green-500 pl-4">
              <h4 className="font-medium text-gray-900">信頼性・継続性</h4>
              <p className="text-sm text-gray-600">32%</p>
            </div>
            <div className="border-l-4 border-yellow-500 pl-4">
              <h4 className="font-medium text-gray-900">デプロイメント</h4>
              <p className="text-sm text-gray-600">20%</p>
            </div>
            <div className="border-l-4 border-red-500 pl-4">
              <h4 className="font-medium text-gray-900">セキュリティ</h4>
              <p className="text-sm text-gray-600">16%</p>
            </div>
            <div className="border-l-4 border-purple-500 pl-4">
              <h4 className="font-medium text-gray-900">ネットワーク</h4>
              <p className="text-sm text-gray-600">12%</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}