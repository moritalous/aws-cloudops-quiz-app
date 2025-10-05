import type { Route } from "./+types/home";
import { Link } from "react-router";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "AWS CloudOps試験対策" },
    { name: "description", content: "AWS Certified CloudOps Engineer - Associate試験対策アプリケーション" },
  ];
}

export default function Home() {
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
            <Link
              to="/quiz?mode=set&count=10"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              10問セットを開始
            </Link>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              エンドレスモード
            </h2>
            <p className="text-gray-600 mb-6">
              時間制限なしで連続して問題に取り組めます。じっくりと学習を進めたい方におすすめです。
            </p>
            <Link
              to="/quiz?mode=endless"
              className="inline-block bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              エンドレスモードを開始
            </Link>
          </div>
        </div>

        {/* ドメイン別学習 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            ドメイン別学習
          </h3>
          <p className="text-gray-600 mb-6">
            特定のドメインに集中して学習したい場合は、以下から選択してください。
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Link
              to="/quiz?mode=set&count=10&domain=monitoring"
              className="border-l-4 border-blue-500 pl-4 py-3 hover:bg-blue-50 transition-colors rounded-r"
            >
              <h4 className="font-medium text-gray-900">監視・ロギング</h4>
              <p className="text-sm text-gray-600">20% - CloudWatch, CloudTrail</p>
            </Link>
            <Link
              to="/quiz?mode=set&count=10&domain=reliability"
              className="border-l-4 border-green-500 pl-4 py-3 hover:bg-green-50 transition-colors rounded-r"
            >
              <h4 className="font-medium text-gray-900">信頼性・継続性</h4>
              <p className="text-sm text-gray-600">32% - Auto Scaling, ELB</p>
            </Link>
            <Link
              to="/quiz?mode=set&count=10&domain=deployment"
              className="border-l-4 border-yellow-500 pl-4 py-3 hover:bg-yellow-50 transition-colors rounded-r"
            >
              <h4 className="font-medium text-gray-900">デプロイメント</h4>
              <p className="text-sm text-gray-600">20% - CodeDeploy, CloudFormation</p>
            </Link>
            <Link
              to="/quiz?mode=set&count=10&domain=security"
              className="border-l-4 border-red-500 pl-4 py-3 hover:bg-red-50 transition-colors rounded-r"
            >
              <h4 className="font-medium text-gray-900">セキュリティ</h4>
              <p className="text-sm text-gray-600">16% - IAM, GuardDuty</p>
            </Link>
            <Link
              to="/quiz?mode=set&count=10&domain=networking"
              className="border-l-4 border-purple-500 pl-4 py-3 hover:bg-purple-50 transition-colors rounded-r"
            >
              <h4 className="font-medium text-gray-900">ネットワーク</h4>
              <p className="text-sm text-gray-600">12% - VPC, Route Tables</p>
            </Link>
          </div>
        </div>

        {/* 試験情報 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            試験について
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">試験形式</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 選択問題（単一回答・複数回答）</li>
                <li>• 試験時間: 180分</li>
                <li>• 問題数: 65問</li>
                <li>• 合格点: 720/1000点</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">学習のコツ</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 各ドメインをバランスよく学習</li>
                <li>• 実際のAWSサービスを触って理解</li>
                <li>• 間違えた問題は解説をしっかり読む</li>
                <li>• 定期的に復習を行う</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
