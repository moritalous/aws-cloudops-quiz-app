import { ErrorHandler } from './error-handler';

export interface NetworkStatus {
  isOnline: boolean;
  connectionType?: string;
  effectiveType?: string;
  downlink?: number;
  rtt?: number;
}

export class NetworkMonitor {
  private static listeners: ((status: NetworkStatus) => void)[] = [];
  private static currentStatus: NetworkStatus = {
    isOnline: navigator.onLine,
  };

  /**
   * ネットワーク監視を開始
   */
  static startMonitoring(): void {
    // オンライン/オフライン状態の監視
    window.addEventListener('online', this.handleOnline.bind(this));
    window.addEventListener('offline', this.handleOffline.bind(this));

    // Network Information API（サポートされている場合）
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;

      if (connection) {
        connection.addEventListener(
          'change',
          this.handleConnectionChange.bind(this)
        );
        this.updateConnectionInfo();
      }
    }

    // Service Worker メッセージの監視
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener(
        'message',
        this.handleServiceWorkerMessage.bind(this)
      );
    }

    // 初期状態を設定
    this.updateStatus();
  }

  /**
   * ネットワーク監視を停止
   */
  static stopMonitoring(): void {
    window.removeEventListener('online', this.handleOnline.bind(this));
    window.removeEventListener('offline', this.handleOffline.bind(this));

    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      if (connection) {
        connection.removeEventListener(
          'change',
          this.handleConnectionChange.bind(this)
        );
      }
    }

    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.removeEventListener(
        'message',
        this.handleServiceWorkerMessage.bind(this)
      );
    }
  }

  /**
   * ネットワーク状態リスナーを追加
   */
  static addListener(listener: (status: NetworkStatus) => void): void {
    this.listeners.push(listener);
  }

  /**
   * ネットワーク状態リスナーを削除
   */
  static removeListener(listener: (status: NetworkStatus) => void): void {
    const index = this.listeners.indexOf(listener);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }

  /**
   * 現在のネットワーク状態を取得
   */
  static getCurrentStatus(): NetworkStatus {
    return { ...this.currentStatus };
  }

  /**
   * ネットワーク接続をテスト
   */
  static async testConnection(): Promise<boolean> {
    try {
      // 小さなリソースをフェッチしてネットワーク接続をテスト
      const response = await fetch('/questions.json', {
        method: 'HEAD',
        cache: 'no-cache',
        signal: AbortSignal.timeout(5000), // 5秒タイムアウト
      });

      return response.ok;
    } catch (error) {
      console.warn('Network connection test failed:', error);
      return false;
    }
  }

  /**
   * オンライン状態の処理
   */
  private static handleOnline(): void {
    console.log('Network: Online');
    this.updateStatus();

    // 接続復旧の通知
    this.notifyListeners();
  }

  /**
   * オフライン状態の処理
   */
  private static handleOffline(): void {
    console.log('Network: Offline');
    this.updateStatus();

    // オフライン通知
    ErrorHandler.handleNetworkError(new Error('Network connection lost'));
    this.notifyListeners();
  }

  /**
   * 接続情報の変更処理
   */
  private static handleConnectionChange(): void {
    console.log('Network: Connection changed');
    this.updateConnectionInfo();
    this.updateStatus();
    this.notifyListeners();
  }

  /**
   * Service Worker メッセージの処理
   */
  private static handleServiceWorkerMessage(event: MessageEvent): void {
    if (event.data && event.data.type === 'OFFLINE_MODE') {
      console.log('Service Worker: Offline mode activated');

      // オフラインモード通知
      const event_custom = new CustomEvent('app-error', {
        detail: {
          message:
            'オフラインモードで動作しています。キャッシュされた問題で学習を続けることができます。',
          type: 'NETWORK_ERROR',
        },
      });
      window.dispatchEvent(event_custom);
    }
  }

  /**
   * ネットワーク状態を更新
   */
  private static updateStatus(): void {
    this.currentStatus.isOnline = navigator.onLine;
    this.updateConnectionInfo();
  }

  /**
   * 接続情報を更新
   */
  private static updateConnectionInfo(): void {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;

      if (connection) {
        this.currentStatus.connectionType = connection.type;
        this.currentStatus.effectiveType = connection.effectiveType;
        this.currentStatus.downlink = connection.downlink;
        this.currentStatus.rtt = connection.rtt;
      }
    }
  }

  /**
   * リスナーに通知
   */
  private static notifyListeners(): void {
    this.listeners.forEach((listener) => {
      try {
        listener(this.getCurrentStatus());
      } catch (error) {
        console.error('Network listener error:', error);
      }
    });
  }

  /**
   * 接続品質を評価
   */
  static getConnectionQuality(): 'excellent' | 'good' | 'poor' | 'offline' {
    if (!this.currentStatus.isOnline) {
      return 'offline';
    }

    const effectiveType = this.currentStatus.effectiveType;
    const rtt = this.currentStatus.rtt;

    if (effectiveType === '4g' && rtt && rtt < 100) {
      return 'excellent';
    } else if (
      effectiveType === '4g' ||
      (effectiveType === '3g' && rtt && rtt < 300)
    ) {
      return 'good';
    } else {
      return 'poor';
    }
  }

  /**
   * 接続品質に基づく推奨設定を取得
   */
  static getRecommendedSettings(): {
    enablePrefetch: boolean;
    cacheStrategy: 'aggressive' | 'moderate' | 'minimal';
    maxConcurrentRequests: number;
  } {
    const quality = this.getConnectionQuality();

    switch (quality) {
      case 'excellent':
        return {
          enablePrefetch: true,
          cacheStrategy: 'aggressive',
          maxConcurrentRequests: 6,
        };
      case 'good':
        return {
          enablePrefetch: true,
          cacheStrategy: 'moderate',
          maxConcurrentRequests: 4,
        };
      case 'poor':
        return {
          enablePrefetch: false,
          cacheStrategy: 'minimal',
          maxConcurrentRequests: 2,
        };
      case 'offline':
      default:
        return {
          enablePrefetch: false,
          cacheStrategy: 'minimal',
          maxConcurrentRequests: 1,
        };
    }
  }
}
