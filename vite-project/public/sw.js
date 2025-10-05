// AWS CloudOps試験対策アプリ - Service Worker
// オフライン対応とキャッシュ管理

const CACHE_NAME = 'aws-cloudops-quiz-v1';
const STATIC_CACHE_NAME = 'aws-cloudops-static-v1';
const DYNAMIC_CACHE_NAME = 'aws-cloudops-dynamic-v1';

// キャッシュするリソース
const STATIC_ASSETS = [
  '/',
  '/quiz',
  '/result',
  '/questions.json',
  '/manifest.json'
];

// キャッシュしないパス
const EXCLUDE_PATHS = [
  '/api/',
  '/admin/',
  '/_vite/',
  '/node_modules/'
];

// Service Worker インストール
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('Service Worker: Static assets cached');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Failed to cache static assets', error);
      })
  );
});

// Service Worker アクティベート
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            // 古いキャッシュを削除
            if (cacheName !== STATIC_CACHE_NAME && 
                cacheName !== DYNAMIC_CACHE_NAME &&
                cacheName.startsWith('aws-cloudops-')) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activated');
        return self.clients.claim();
      })
  );
});

// フェッチイベント処理
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  
  // 除外パスをスキップ
  if (EXCLUDE_PATHS.some(path => url.pathname.startsWith(path))) {
    return;
  }
  
  // GET リクエストのみ処理
  if (request.method !== 'GET') {
    return;
  }
  
  event.respondWith(
    handleFetchRequest(request)
  );
});

// フェッチリクエスト処理
async function handleFetchRequest(request) {
  const url = new URL(request.url);
  
  try {
    // 静的アセットの場合
    if (isStaticAsset(url.pathname)) {
      return await handleStaticAsset(request);
    }
    
    // 問題データの場合
    if (url.pathname === '/questions.json') {
      return await handleQuestionData(request);
    }
    
    // その他のリクエスト
    return await handleDynamicRequest(request);
    
  } catch (error) {
    console.error('Service Worker: Fetch failed', error);
    return await handleOfflineResponse(request);
  }
}

// 静的アセット処理
async function handleStaticAsset(request) {
  // キャッシュファーストストラテジー
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    // バックグラウンドで更新
    updateCache(request);
    return cachedResponse;
  }
  
  // キャッシュにない場合はネットワークから取得
  const networkResponse = await fetch(request);
  
  if (networkResponse.ok) {
    const cache = await caches.open(STATIC_CACHE_NAME);
    cache.put(request, networkResponse.clone());
  }
  
  return networkResponse;
}

// 問題データ処理
async function handleQuestionData(request) {
  try {
    // ネットワークファーストストラテジー
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
    
  } catch (error) {
    // ネットワークエラーの場合はキャッシュから返す
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      // オフライン通知をクライアントに送信
      notifyOfflineMode();
      return cachedResponse;
    }
    
    throw error;
  }
}

// 動的リクエスト処理
async function handleDynamicRequest(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
    
  } catch (error) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    throw error;
  }
}

// オフライン時のレスポンス処理
async function handleOfflineResponse(request) {
  const url = new URL(request.url);
  
  // HTMLページの場合
  if (request.headers.get('accept')?.includes('text/html')) {
    const cachedPage = await caches.match('/');
    if (cachedPage) {
      return cachedPage;
    }
    
    return new Response(
      createOfflinePage(),
      {
        status: 200,
        headers: { 'Content-Type': 'text/html' }
      }
    );
  }
  
  // その他のリソース
  return new Response(
    JSON.stringify({ error: 'Offline - Resource not available' }),
    {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    }
  );
}

// 静的アセット判定
function isStaticAsset(pathname) {
  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2'];
  return staticExtensions.some(ext => pathname.endsWith(ext));
}

// キャッシュ更新（バックグラウンド）
async function updateCache(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE_NAME);
      cache.put(request, networkResponse);
    }
  } catch (error) {
    // バックグラウンド更新の失敗は無視
    console.log('Background cache update failed:', error);
  }
}

// オフライン通知
function notifyOfflineMode() {
  self.clients.matchAll().then(clients => {
    clients.forEach(client => {
      client.postMessage({
        type: 'OFFLINE_MODE',
        message: 'オフラインモードで動作しています'
      });
    });
  });
}

// オフラインページHTML生成
function createOfflinePage() {
  return `
    <!DOCTYPE html>
    <html lang="ja">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>オフライン - AWS CloudOps試験対策</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          margin: 0;
          padding: 20px;
          background-color: #f9fafb;
          color: #374151;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
        }
        .container {
          max-width: 400px;
          text-align: center;
          background: white;
          padding: 40px;
          border-radius: 8px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .icon {
          width: 64px;
          height: 64px;
          margin: 0 auto 20px;
          background-color: #fef3c7;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        h1 {
          margin: 0 0 16px;
          font-size: 24px;
          font-weight: 600;
        }
        p {
          margin: 0 0 24px;
          color: #6b7280;
          line-height: 1.5;
        }
        button {
          background-color: #3b82f6;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 6px;
          font-size: 16px;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        button:hover {
          background-color: #2563eb;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="icon">
          <svg width="32" height="32" fill="#f59e0b" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
        <h1>オフラインモード</h1>
        <p>
          インターネット接続がありません。<br>
          キャッシュされた問題で学習を続けることができます。
        </p>
        <button onclick="window.location.href='/'">
          アプリに戻る
        </button>
      </div>
    </body>
    </html>
  `;
}

// ネットワーク状態変更の監視
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

console.log('Service Worker: Loaded');