# AWS CloudOps 試験対策アプリ

AWS Certified CloudOps Engineer - Associate試験対策のためのSingle Page Application (SPA)です。

## 機能

- **10問セットモード**: 10問の問題で集中学習
- **エンドレスモード**: 時間制限なしの継続学習
- **即座のフィードバック**: 各問題に詳細な解説付き
- **レスポンシブデザイン**: デスクトップ・スマートフォン対応
- **セッション管理**: ブラウザリロード時に初期化

## 技術スタック

- React 19 + TypeScript
- React Router v7
- Tailwind CSS
- Vite
- Vitest (テスト)

## 開発

```bash
# 依存関係のインストール
npm install

# 開発サーバー起動
npm run dev

# ビルド
npm run build

# テスト実行
npm run test

# リント
npm run lint
```

## プロジェクト構造

```
app/
├── components/     # 再利用可能なUIコンポーネント
├── hooks/         # カスタムReactフック
├── routes/        # ページコンポーネント
├── types/         # TypeScript型定義
├── utils/         # ユーティリティ関数
└── app.css        # グローバルスタイル
```

A modern, production-ready template for building full-stack React applications using React Router.

[![Open in StackBlitz](https://developer.stackblitz.com/img/open_in_stackblitz.svg)](https://stackblitz.com/github/remix-run/react-router-templates/tree/main/default)

## Features

- 🚀 Server-side rendering
- ⚡️ Hot Module Replacement (HMR)
- 📦 Asset bundling and optimization
- 🔄 Data loading and mutations
- 🔒 TypeScript by default
- 🎉 TailwindCSS for styling
- 📖 [React Router docs](https://reactrouter.com/)

## Getting Started

### Installation

Install the dependencies:

```bash
npm install
```

### Development

Start the development server with HMR:

```bash
npm run dev
```

Your application will be available at `http://localhost:5173`.

## Building for Production

Create a production build:

```bash
npm run build
```

## Deployment

### Docker Deployment

To build and run using Docker:

```bash
docker build -t my-app .

# Run the container
docker run -p 3000:3000 my-app
```

The containerized application can be deployed to any platform that supports Docker, including:

- AWS ECS
- Google Cloud Run
- Azure Container Apps
- Digital Ocean App Platform
- Fly.io
- Railway

### DIY Deployment

If you're familiar with deploying Node applications, the built-in app server is production-ready.

Make sure to deploy the output of `npm run build`

```
├── package.json
├── package-lock.json (or pnpm-lock.yaml, or bun.lockb)
├── build/
│   ├── client/    # Static assets
│   └── server/    # Server-side code
```

## Styling

This template comes with [Tailwind CSS](https://tailwindcss.com/) already configured for a simple default starting experience. You can use whatever CSS framework you prefer.

---

Built with ❤️ using React Router.
