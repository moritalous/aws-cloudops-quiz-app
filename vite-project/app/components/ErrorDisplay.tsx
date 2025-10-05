import { useNavigate } from 'react-router';

interface ErrorDisplayProps {
  title?: string;
  message: string;
  showRetry?: boolean;
  showHome?: boolean;
  onRetry?: () => void;
}

export function ErrorDisplay({ 
  title = 'エラーが発生しました',
  message,
  showRetry = false,
  showHome = true,
  onRetry
}: ErrorDisplayProps) {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          {/* エラーアイコン */}
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
            <svg
              className="h-6 w-6 text-red-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>

          {/* エラータイトル */}
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            {title}
          </h2>

          {/* エラーメッセージ */}
          <p className="text-gray-600 mb-6">
            {message}
          </p>

          {/* アクションボタン */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            {showRetry && onRetry && (
              <button
                onClick={onRetry}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                再試行
              </button>
            )}
            
            {showHome && (
              <button
                onClick={() => navigate('/')}
                className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition-colors font-medium"
              >
                メニューに戻る
              </button>
            )}
          </div>
        </div>

        {/* 追加のヘルプ情報 */}
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-500">
            問題が続く場合は、ページを再読み込みしてください。
          </p>
        </div>
      </div>
    </div>
  );
}

// 特定のエラータイプ用のプリセットコンポーネント

export function NetworkErrorDisplay({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorDisplay
      title="接続エラー"
      message="インターネット接続を確認して、もう一度お試しください。"
      showRetry={true}
      onRetry={onRetry}
    />
  );
}

export function DataLoadErrorDisplay({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorDisplay
      title="データ読み込みエラー"
      message="問題データの読み込みに失敗しました。しばらく後にお試しください。"
      showRetry={true}
      onRetry={onRetry}
    />
  );
}

export function NotFoundErrorDisplay() {
  return (
    <ErrorDisplay
      title="ページが見つかりません"
      message="お探しのページは存在しないか、移動された可能性があります。"
      showRetry={false}
    />
  );
}