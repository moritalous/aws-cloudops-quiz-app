# Implementation Plan

- [ ] 1. React Router設定をSPAモードに変更
  - react-router.config.tsでssr: falseに設定
  - 設定変更後の動作確認
  - _Requirements: 1.1, 1.2_

- [ ] 2. GitHub Pages用ビルドスクリプトを作成
  - [ ] 2.1 ビルドスクリプトファイルの作成
    - scripts/build-gh-pages.jsファイルを作成
    - 必要なNode.jsモジュールのimport設定
    - _Requirements: 3.1, 3.2_

  - [ ] 2.2 ディレクトリクリア機能の実装
    - 既存../docsディレクトリの削除処理
    - エラーハンドリングの実装
    - _Requirements: 3.1_

  - [ ] 2.3 React Routerビルド実行機能の実装
    - child_processを使用したreact-router buildコマンド実行
    - ビルド成功/失敗の判定処理
    - _Requirements: 1.1, 3.2_

  - [ ] 2.4 ファイルコピー機能の実装
    - build/clientから../docsへの再帰的コピー
    - ファイル権限とタイムスタンプの保持
    - _Requirements: 1.2, 3.2_

- [ ] 3. SPA routing対応の404.htmlを実装
  - [ ] 3.1 404.htmlテンプレートの作成
    - spa-github-pagesソリューションベースの404.html作成
    - URLリダイレクト用JavaScriptの実装
    - _Requirements: 2.1, 2.2_

  - [ ] 3.2 index.htmlにリダイレクト処理を追加
    - クエリパラメータからURLを復元するスクリプト追加
    - ブラウザ履歴の適切な処理
    - _Requirements: 2.2, 2.3_

- [ ] 4. package.jsonスクリプトの追加
  - build:gh-pagesスクリプトの追加
  - スクリプト実行の動作確認
  - _Requirements: 3.3_

- [ ] 5. Vite設定でbase pathを調整
  - vite.config.tsでGitHub Pages用のbase設定
  - 本番環境とローカル環境の設定分岐
  - _Requirements: 1.3_

- [ ] 6. ローカルテスト環境の構築
  - [ ] 6.1 静的サーバーでのテスト
    - docsディレクトリをローカルで配信
    - 各ルートへの直接アクセステスト
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ]* 6.2 ビルドプロセスのテスト
    - build:gh-pagesコマンドの実行テスト
    - 生成ファイルの検証
    - _Requirements: 3.1, 3.2, 3.3_

- [ ] 7. ドキュメントの更新
  - README.mdにGitHub Pages設定手順を追加
  - トラブルシューティング情報の記載
  - _Requirements: 4.1, 4.2, 4.3_