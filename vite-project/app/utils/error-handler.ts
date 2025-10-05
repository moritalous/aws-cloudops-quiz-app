import type { AppError, ErrorTypes } from '~/types';

export class ErrorHandler {
  private static errorListeners: ((error: AppError) => void)[] = [];

  /**
   * エラーリスナーを追加
   */
  static addErrorListener(listener: (error: AppError) => void): void {
    this.errorListeners.push(listener);
  }

  /**
   * エラーリスナーを削除
   */
  static removeErrorListener(listener: (error: AppError) => void): void {
    const index = this.errorListeners.indexOf(listener);
    if (index > -1) {
      this.errorListeners.splice(index, 1);
    }
  }

  /**
   * エラーを処理
   */
  static handleError(error: AppError): void {
    // コンソールにエラーログを出力
    console.error('Application Error:', {
      type: error.type,
      message: error.message,
      timestamp: error.timestamp,
      details: error.details,
    });

    // エラーをローカルストレージに記録（デバッグ用）
    this.logErrorToStorage(error);

    // ユーザーフレンドリーなメッセージを取得
    const userMessage = this.getUserMessage(error);

    // 登録されたリスナーに通知
    this.errorListeners.forEach((listener) => {
      try {
        listener(error);
      } catch (listenerError) {
        console.error('Error in error listener:', listenerError);
      }
    });

    // ユーザーにエラーメッセージを表示
    this.showErrorToUser(userMessage, error.type);
  }

  /**
   * ユーザーフレンドリーなエラーメッセージを取得
   */
  static getUserMessage(error: AppError): string {
    switch (error.type) {
      case 'NETWORK_ERROR':
        return 'ネットワーク接続に問題があります。インターネット接続を確認してください。';
      case 'DATA_LOAD_ERROR':
        return '問題データの読み込みに失敗しました。ページを再読み込みしてください。';
      case 'SESSION_ERROR':
        return 'セッションに問題が発生しました。新しいセッションを開始してください。';
      case 'VALIDATION_ERROR':
        return '入力データに問題があります。もう一度お試しください。';
      case 'COMPONENT_ERROR':
        return 'アプリケーションでエラーが発生しました。ページを再読み込みしてください。';
      default:
        return '予期しないエラーが発生しました。ページを再読み込みしてください。';
    }
  }

  /**
   * ユーザーにエラーメッセージを表示
   */
  private static showErrorToUser(message: string, type: ErrorTypes): void {
    // カスタムイベントを発火してUIコンポーネントに通知
    const event = new CustomEvent('app-error', {
      detail: { message, type },
    });
    window.dispatchEvent(event);
  }

  /**
   * エラーをローカルストレージに記録
   */
  private static logErrorToStorage(error: AppError): void {
    try {
      const errorLog = {
        ...error,
        timestamp: error.timestamp.toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      };

      const existingLogs = this.getErrorLogs();
      existingLogs.push(errorLog);

      // 最新の10件のみ保持
      const recentLogs = existingLogs.slice(-10);

      localStorage.setItem('app_error_logs', JSON.stringify(recentLogs));
    } catch (storageError) {
      console.warn('Failed to log error to storage:', storageError);
    }
  }

  /**
   * ローカルストレージからエラーログを取得
   */
  static getErrorLogs(): any[] {
    try {
      const logs = localStorage.getItem('app_error_logs');
      return logs ? JSON.parse(logs) : [];
    } catch (error) {
      console.warn('Failed to retrieve error logs:', error);
      return [];
    }
  }

  /**
   * エラーログをクリア
   */
  static clearErrorLogs(): void {
    try {
      localStorage.removeItem('app_error_logs');
    } catch (error) {
      console.warn('Failed to clear error logs:', error);
    }
  }

  /**
   * 一般的なエラーからAppErrorを作成
   */
  static createAppError(
    type: ErrorTypes,
    message: string,
    details?: any
  ): AppError {
    return {
      type,
      message,
      details,
      timestamp: new Date(),
    };
  }

  /**
   * ネットワークエラーを処理
   */
  static handleNetworkError(error: any): void {
    const appError = this.createAppError(
      'NETWORK_ERROR',
      'Network request failed',
      error
    );
    this.handleError(appError);
  }

  /**
   * データ読み込みエラーを処理
   */
  static handleDataLoadError(error: any): void {
    const appError = this.createAppError(
      'DATA_LOAD_ERROR',
      'Failed to load application data',
      error
    );
    this.handleError(appError);
  }

  /**
   * セッションエラーを処理
   */
  static handleSessionError(error: any): void {
    const appError = this.createAppError(
      'SESSION_ERROR',
      'Session management error',
      error
    );
    this.handleError(appError);
  }

  /**
   * バリデーションエラーを処理
   */
  static handleValidationError(error: any): void {
    const appError = this.createAppError(
      'VALIDATION_ERROR',
      'Data validation failed',
      error
    );
    this.handleError(appError);
  }

  /**
   * コンポーネントエラーを処理
   */
  static handleComponentError(error: any, errorInfo?: any): void {
    const appError = this.createAppError(
      'COMPONENT_ERROR',
      'React component error',
      { error, errorInfo }
    );
    this.handleError(appError);
  }
}
