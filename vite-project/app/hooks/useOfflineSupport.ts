import { useState, useEffect, useCallback } from 'react';
import { SessionRecovery } from '~/utils/session-recovery';
import { NetworkMonitor, type NetworkStatus } from '~/utils/network-monitor';
import { ServiceWorkerManager } from '~/utils/service-worker-manager';
import type { SessionData } from '~/types';

interface OfflineSupportState {
  isOnline: boolean;
  networkStatus: NetworkStatus;
  serviceWorkerStatus: {
    isSupported: boolean;
    isRegistered: boolean;
    isActive: boolean;
    hasUpdate: boolean;
  };
  cacheSize: number;
  sessionRecoveryStats: {
    hasMainSession: boolean;
    hasBackupSession: boolean;
    mainSessionValid: boolean;
    backupSessionValid: boolean;
    lastBackupTime: Date | null;
  };
}

export function useOfflineSupport() {
  const [state, setState] = useState<OfflineSupportState>({
    isOnline: navigator.onLine,
    networkStatus: NetworkMonitor.getCurrentStatus(),
    serviceWorkerStatus: ServiceWorkerManager.getStatus(),
    cacheSize: 0,
    sessionRecoveryStats: SessionRecovery.getRecoveryStats()
  });

  // ネットワーク状態の監視
  useEffect(() => {
    const handleNetworkChange = (networkStatus: NetworkStatus) => {
      setState(prev => ({
        ...prev,
        isOnline: networkStatus.isOnline,
        networkStatus
      }));
    };

    NetworkMonitor.addListener(handleNetworkChange);
    NetworkMonitor.startMonitoring();

    return () => {
      NetworkMonitor.removeListener(handleNetworkChange);
      NetworkMonitor.stopMonitoring();
    };
  }, []);

  // Service Worker の初期化
  useEffect(() => {
    const initializeServiceWorker = async () => {
      await ServiceWorkerManager.initializeOfflineSupport();
      
      setState(prev => ({
        ...prev,
        serviceWorkerStatus: ServiceWorkerManager.getStatus()
      }));
    };

    initializeServiceWorker();
  }, []);

  // セッション復旧の自動バックアップ設定
  useEffect(() => {
    SessionRecovery.setupAutoBackup();
  }, []);

  // キャッシュサイズの定期更新
  useEffect(() => {
    const updateCacheSize = async () => {
      const size = await ServiceWorkerManager.getCacheSize();
      setState(prev => ({
        ...prev,
        cacheSize: size
      }));
    };

    updateCacheSize();
    
    // 5分間隔で更新
    const interval = setInterval(updateCacheSize, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  // セッション復旧統計の定期更新
  useEffect(() => {
    const updateRecoveryStats = () => {
      setState(prev => ({
        ...prev,
        sessionRecoveryStats: SessionRecovery.getRecoveryStats()
      }));
    };

    updateRecoveryStats();
    
    // 1分間隔で更新
    const interval = setInterval(updateRecoveryStats, 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  // セッション復旧を試行
  const attemptSessionRecovery = useCallback((): SessionData | null => {
    const recoveredSession = SessionRecovery.attemptRecovery();
    
    // 統計を更新
    setState(prev => ({
      ...prev,
      sessionRecoveryStats: SessionRecovery.getRecoveryStats()
    }));

    return recoveredSession;
  }, []);

  // セッションバックアップを作成
  const createSessionBackup = useCallback((session: SessionData): void => {
    SessionRecovery.createBackup(session);
    
    // 統計を更新
    setState(prev => ({
      ...prev,
      sessionRecoveryStats: SessionRecovery.getRecoveryStats()
    }));
  }, []);

  // 全セッションをクリア
  const clearAllSessions = useCallback((): void => {
    SessionRecovery.clearAllSessions();
    
    // 統計を更新
    setState(prev => ({
      ...prev,
      sessionRecoveryStats: SessionRecovery.getRecoveryStats()
    }));
  }, []);

  // ネットワーク接続をテスト
  const testNetworkConnection = useCallback(async (): Promise<boolean> => {
    const isConnected = await NetworkMonitor.testConnection();
    
    // 状態を更新
    setState(prev => ({
      ...prev,
      isOnline: isConnected,
      networkStatus: { ...prev.networkStatus, isOnline: isConnected }
    }));

    return isConnected;
  }, []);

  // Service Worker を更新
  const updateServiceWorker = useCallback(async (): Promise<void> => {
    await ServiceWorkerManager.activateNewServiceWorker();
  }, []);

  // キャッシュをクリア
  const clearCache = useCallback(async (): Promise<void> => {
    await ServiceWorkerManager.clearCache();
    
    // キャッシュサイズを更新
    const size = await ServiceWorkerManager.getCacheSize();
    setState(prev => ({
      ...prev,
      cacheSize: size
    }));
  }, []);

  // 接続品質を取得
  const getConnectionQuality = useCallback(() => {
    return NetworkMonitor.getConnectionQuality();
  }, []);

  // 推奨設定を取得
  const getRecommendedSettings = useCallback(() => {
    return NetworkMonitor.getRecommendedSettings();
  }, []);

  // キャッシュサイズを人間が読みやすい形式に変換
  const formatCacheSize = useCallback((bytes: number): string => {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }, []);

  // オフライン対応の状態を取得
  const getOfflineCapabilities = useCallback(() => {
    const { serviceWorkerStatus, cacheSize, sessionRecoveryStats } = state;
    
    return {
      canWorkOffline: serviceWorkerStatus.isActive && cacheSize > 0,
      hasSessionBackup: sessionRecoveryStats.hasBackupSession && sessionRecoveryStats.backupSessionValid,
      cacheStatus: cacheSize > 0 ? 'available' : 'empty',
      lastBackupTime: sessionRecoveryStats.lastBackupTime
    };
  }, [state]);

  return {
    // 状態
    ...state,
    
    // セッション復旧関数
    attemptSessionRecovery,
    createSessionBackup,
    clearAllSessions,
    
    // ネットワーク関数
    testNetworkConnection,
    getConnectionQuality,
    getRecommendedSettings,
    
    // Service Worker 関数
    updateServiceWorker,
    clearCache,
    
    // ユーティリティ関数
    formatCacheSize,
    getOfflineCapabilities
  };
}