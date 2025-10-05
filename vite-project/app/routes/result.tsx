import { useLocation, useNavigate } from 'react-router';
import type { Route } from "./+types/result";
import type { SessionData, QuizStatistics } from '~/types';

export function meta({}: Route.MetaArgs) {
  return [
    { title: "結果 - AWS CloudOps試験対策" },
    { name: "description", content: "クイズの結果と統計" },
  ];
}

export default function Result() {
  const location = useLocation();
  const navigate = useNavigate();
  
  const { session, statistics } = location.state as { 
    session: SessionData; 
    statistics: QuizStatistics;
  } || {};

  if (!session || !statistics) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              結果データが見つかりません
            </h2>
            <p className="text-gray-600 mb-6">
              セッションデータが利用できません。新しいクイズを開始してください。
            </p>
            <button
              onClick={() => navigate('/')}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              ホームに戻る
            </button>
          </div>
        </div>
      </div>
    );
  }

  const sessionDuration = Math.floor((new Date().getTime() - session.startedAt.getTime()) / 1000);
  const minutes = Math.floor(sessionDuration / 60);
  const seconds = sessionDuration % 60;

  const getScoreColor = (accuracy: number) => {
    if (accuracy >= 80) return 'text-green-600';
    if (accuracy >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreMessage = (accuracy: number) => {
    if (accuracy >= 80) return '素晴らしい結果です！';
    if (accuracy >= 60) return 'よくできました！';
    return 'もう少し頑張りましょう！';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          クイズ結果
        </h1>

        {/* 総合スコア */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="text-center">
            <div className={`text-6xl font-bold mb-4 ${getScoreColor(statistics.accuracy)}`}>
              {Math.round(statistics.accuracy)}%
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              {getScoreMessage(statistics.accuracy)}
            </h2>
            <p className="text-gray-600">
              {statistics.correctAnswers} / {statistics.totalQuestions} 問正解
            </p>
          </div>
        </div>

        {/* 詳細統計 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* セッション情報 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              セッション情報
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">モード:</span>
                <span className="font-medium">
                  {session.mode === 'set' ? '10問セット' : 'エンドレス'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">所要時間:</span>
                <span className="font-medium">
                  {minutes}分{seconds}秒
                </span>
              </div>
              {statistics.averageTimePerQuestion && (
                <div className="flex justify-between">
                  <span className="text-gray-600">平均回答時間:</span>
                  <span className="font-medium">
                    {Math.round(statistics.averageTimePerQuestion)}秒
                  </span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-600">開始時刻:</span>
                <span className="font-medium">
                  {session.startedAt.toLocaleTimeString()}
                </span>
              </div>
            </div>
          </div>

          {/* パフォーマンス分析 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              パフォーマンス分析
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">正解数:</span>
                <span className="font-medium text-green-600">
                  {statistics.correctAnswers}問
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">不正解数:</span>
                <span className="font-medium text-red-600">
                  {statistics.totalQuestions - statistics.correctAnswers}問
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">正答率:</span>
                <span className={`font-medium ${getScoreColor(statistics.accuracy)}`}>
                  {Math.round(statistics.accuracy)}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* ドメイン別成績 */}
        {Object.keys(statistics.domainBreakdown).length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              ドメイン別成績
            </h3>
            <div className="space-y-4">
              {Object.entries(statistics.domainBreakdown).map(([domain, stats]) => (
                <div key={domain} className="border-b border-gray-200 pb-3 last:border-b-0">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-gray-900">{domain}</span>
                    <span className={`font-medium ${getScoreColor(stats.accuracy)}`}>
                      {Math.round(stats.accuracy)}%
                    </span>
                  </div>
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>{stats.correct} / {stats.total} 問正解</span>
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${stats.accuracy}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* アクションボタン */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => navigate('/')}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            新しいクイズを開始
          </button>
          <button
            onClick={() => navigate(`/quiz?mode=${session.mode}&count=${session.targetQuestionCount || 10}`)}
            className="bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 transition-colors font-medium"
          >
            同じ設定で再挑戦
          </button>
          <button
            onClick={() => window.print()}
            className="bg-gray-600 text-white px-8 py-3 rounded-lg hover:bg-gray-700 transition-colors font-medium"
          >
            結果を印刷
          </button>
        </div>
      </div>
    </div>
  );
}