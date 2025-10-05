import { ErrorHandler } from './error-handler';

export class ServiceWorkerManager {
  private static registration: ServiceWorkerRegistration | null = null;
  private static isSupported = 'serviceWorker' in navigator;

  /**
   * Service Worker を登録
   */
  static async register(): Promise<boolean> {
    if (!this.isSupported) {
      console.warn('Service Worker is not supported');
      return false;
    }

    try {
      console.log('Service Worker: Registering...');
      
      this.registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });

      console.log('Service Worker: Registered successfully', this.registration);

      // 更新チェック
      this.registration.addEventListener('updatefound', this.handleUpdateFound.bind(this));

      // アクティブなService Workerの状態変更を監視
      if (this.registration.active) {
        this.registration.active.addEventListener('statechange', this.handleStateChange.bind(this));
      }

      // 定期的な更新チェック（1時間間隔）
      setInterval(() => {
        this.checkForUpdates();
      }, 60 * 60 * 1000);

      return true;

    } catch (error) {
      console.error('Service Worker: Registration failed', error);
      ErrorHandler.handleNetworkError(error);
      return false;
    }
  }

  /**
   * Service Worker の登録を解除
   */
  static async unregister(): Promise<boolean> {
    if (!this.isSupported || !this.registration) {
      return false;
    }

    try {
      const result = await this.registration.unregister();
      console.log('Service Worker: Unregistered', result);
      this.registration = null;
      return result;
    } catch (error) {
      console.error('Service Worker: Unregistration failed', error);
      return false;
    }
  }

  /**
   * Service Worker の更新をチェック
   */
  static async checkForUpdates(): Promise<void> {
    if (!this.registration) {
      return;
    }

    try {
      await this.registration.update();
      console.log('Service Worker: Update check completed');
    } catch (error) {
      console.warn('Service Worker: Update check failed', error);
    }
  }

  /**
   * 新しい Service Worker をアクティベート
   */
  static async activateNewServiceWorker(): Promise<void> {
    if (!this.registration || !this.registration.waiting) {
      return;
    }

    try {
      // 新しいService Workerにスキップ待機メッセージを送信
      this.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
      
      // ページをリロード
      window.location.reload();
    } catch (error) {
      console.error('Service Worker: Failed to activate new service worker', error);
    }
  }

  /**
   * Service Worker にメッセージを送信
   */
  static async sendMessage(message: any): Promise<void> {
    if (!this.registration || !this.registration.active) {
      return;
    }

    try {
      this.registration.active.postMessage(message);
    } catch (error) {
      console.error('Service Worker: Failed to send message', error);
    }
  }

  /**
   * キャッシュをクリア
   */
  static async clearCache(): Promise<void> {
    if (!('caches' in window)) {
      return;
    }

    try {
      const cacheNames = await caches.keys();
      
      await Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName.startsWith('aws-cloudops-')) {
            console.log('Clearing cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );

      console.log('Service Worker: Cache cleared');
    } catch (error) {
      console.error('Service Worker: Failed to clear cache', error);
    }
  }

  /**
   * キャッシュサイズを取得
   */
  static async getCacheSize(): Promise<number> {
    if (!('caches' in window)) {
      return 0;
    }

    try {
      const cacheNames = await caches.keys();
      let totalSize = 0;

      for (const cacheName of cacheNames) {
        if (cacheName.startsWith('aws-cloudops-')) {
          const cache = await caches.open(cacheName);
          const requests = await cache.keys();
          
          for (const request of requests) {
            const response = await cache.match(request);
            if (response) {
              const blob = await response.blob();
              totalSize += blob.size;
            }
          }
        }
      }

      return totalSize;
    } catch (error) {
      console.error('Service Worker: Failed to calculate cache size', error);
      return 0;
    }
  }

  /**
   * Service Worker の状態を取得
   */
  static getStatus(): {
    isSupported: boolean;
    isRegistered: boolean;
    isActive: boolean;
    hasUpdate: boolean;
  } {
    return {
      isSupported: this.isSupported,
      isRegistered: !!this.registration,
      isActive: !!(this.registration && this.registration.active),
      hasUpdate: !!(this.registration && this.registration.waiting)
    };
  }

  /**
   * 更新発見時の処理
   */
  private static handleUpdateFound(): void {
    if (!this.registration) return;

    const newWorker = this.registration.installing;
    if (!newWorker) return;

    console.log('Service Worker: Update found');

    newWorker.addEventListener('statechange', () => {
      if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
        console.log('Service Worker: New version available');
        
        // ユーザーに更新通知
        this.notifyUpdate();
      }
    });
  }

  /**
   * 状態変更時の処理
   */
  private static handleStateChange(event: Event): void {
    const worker = event.target as ServiceWorker;
    console.log('Service Worker: State changed to', worker.state);
  }

  /**
   * 更新通知
   */
  private static notifyUpdate(): void {
    const event = new CustomEvent('app-error', {
      detail: { 
        message: 'アプリケーションの新しいバージョンが利用可能です。ページを再読み込みして更新してください。', 
        type: 'VALIDATION_ERROR' 
      }
    });
    window.dispatchEvent(event);
  }

  /**
   * オフライン対応の初期化
   */
  static async initializeOfflineSupport(): Promise<void> {
    // Service Worker を登録
    const registered = await this.register();
    
    if (registered) {
      console.log('Service Worker: Offline support initialized');
      
      // 重要なリソースを事前キャッシュ
      await this.precacheImportantResources();
    }
  }

  /**
   * 重要なリソースを事前キャッシュ
   */
  private static async precacheImportantResources(): Promise<void> {
    if (!('caches' in window)) {
      return;
    }

    try {
      const cache = await caches.open('aws-cloudops-precache-v1');
      
      const importantResources = [
        '/questions.json',
        '/',
        '/quiz',
        '/result'
      ];

      // リソースを順次キャッシュ（並行処理でサーバーに負荷をかけないため）
      for (const resource of importantResources) {
        try {
          await cache.add(resource);
          console.log('Precached:', resource);
        } catch (error) {
          console.warn('Failed to precache:', resource, error);
        }
      }

    } catch (error) {
      console.error('Service Worker: Precaching failed', error);
    }
  }
}