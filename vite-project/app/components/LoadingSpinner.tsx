interface LoadingSpinnerProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
  fullScreen?: boolean;
}

export function LoadingSpinner({
  message = '読み込み中...',
  size = 'medium',
  fullScreen = false,
}: LoadingSpinnerProps) {
  const sizeClasses = {
    small: 'h-6 w-6',
    medium: 'h-12 w-12',
    large: 'h-16 w-16',
  };

  const containerClasses = fullScreen
    ? 'min-h-screen bg-gray-50 flex items-center justify-center'
    : 'flex items-center justify-center p-8';

  return (
    <div className={containerClasses}>
      <div className="text-center">
        <div
          className={`animate-spin rounded-full border-b-2 border-blue-600 mx-auto mb-4 ${sizeClasses[size]}`}
        ></div>
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );
}

// プリセットローディングコンポーネント

export function QuestionLoadingSpinner() {
  return (
    <LoadingSpinner
      message="問題を読み込み中..."
      size="medium"
      fullScreen={true}
    />
  );
}

export function DataValidationSpinner() {
  return (
    <LoadingSpinner
      message="データを検証中..."
      size="medium"
      fullScreen={true}
    />
  );
}
