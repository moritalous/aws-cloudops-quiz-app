#!/usr/bin/env node

import { execSync } from 'child_process';
import { existsSync, rmSync, cpSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// プロジェクトルートディレクトリ（vite-project）
const projectRoot = dirname(__dirname);
// ワークスペースルートディレクトリ（vite-projectの親）
const workspaceRoot = dirname(projectRoot);
// 出力先ディレクトリ（ワークスペースルート/docs）
const docsDir = join(workspaceRoot, 'docs');
// ビルド結果ディレクトリ
const buildClientDir = join(projectRoot, 'build', 'client');

console.log('🚀 GitHub Pages用ビルドを開始します...');
console.log(`プロジェクトルート: ${projectRoot}`);
console.log(`出力先: ${docsDir}`);
/**
 * 既存のdocsディレクトリをクリアする
 */
function clearDocsDirectory() {
  try {
    if (existsSync(docsDir)) {
      console.log('📁 既存のdocsディレクトリを削除中...');
      rmSync(docsDir, { recursive: true, force: true });
      console.log('✅ docsディレクトリを削除しました');
    } else {
      console.log('📁 docsディレクトリは存在しません（初回実行）');
    }
  } catch (error) {
    console.error('❌ docsディレクトリの削除に失敗しました:', error.message);
    process.exit(1);
  }
}

/**
 * React Routerビルドを実行する
 */
function runReactRouterBuild() {
  try {
    console.log('🔨 React Routerビルドを実行中...');
    
    // GitHub Pages用の環境変数を設定
    const env = {
      ...process.env,
      NODE_ENV: 'production'
    };
    
    console.log('🔧 GitHub Pages base path: /aws-cloudops-quiz-app/');
    
    // プロジェクトディレクトリでnpm run buildを実行
    execSync('npm run build', {
      cwd: projectRoot,
      stdio: 'inherit',
      encoding: 'utf8',
      env
    });
    
    console.log('✅ React Routerビルドが完了しました');
    
    // ビルド結果ディレクトリの存在確認
    if (!existsSync(buildClientDir)) {
      throw new Error(`ビルド結果ディレクトリが見つかりません: ${buildClientDir}`);
    }
    
    console.log('✅ ビルド結果ディレクトリを確認しました');
    
  } catch (error) {
    console.error('❌ React Routerビルドに失敗しました:', error.message);
    process.exit(1);
  }
}

/**
 * ビルド結果をdocsディレクトリにコピーする
 */
function copyBuildToDocsDirectory() {
  try {
    console.log('📋 ビルド結果をdocsディレクトリにコピー中...');
    
    // docsディレクトリを作成
    mkdirSync(docsDir, { recursive: true });
    
    // build/clientの内容をdocsディレクトリに再帰的にコピー
    cpSync(buildClientDir, docsDir, {
      recursive: true,
      preserveTimestamps: true,
      force: true
    });
    
    console.log('✅ ファイルコピーが完了しました');
    console.log(`📁 出力先: ${docsDir}`);
    
  } catch (error) {
    console.error('❌ ファイルコピーに失敗しました:', error.message);
    process.exit(1);
  }
}

/**
 * メイン実行関数
 */
function main() {
  try {
    console.log('🎯 GitHub Pages用ビルドプロセスを開始します\n');
    
    // 1. 既存のdocsディレクトリをクリア
    clearDocsDirectory();
    
    // 2. React Routerビルドを実行
    runReactRouterBuild();
    
    // 3. ビルド結果をdocsディレクトリにコピー
    copyBuildToDocsDirectory();
    
    console.log('\n🎉 GitHub Pages用ビルドが正常に完了しました！');
    console.log('📝 次のステップ:');
    console.log('   1. docsディレクトリの内容を確認してください');
    console.log('   2. GitHub Pagesの設定でdocsディレクトリを指定してください');
    
  } catch (error) {
    console.error('\n💥 ビルドプロセスでエラーが発生しました:', error.message);
    process.exit(1);
  }
}

// スクリプトが直接実行された場合のみmain関数を実行
// Windows環境でのパス比較を修正
const scriptPath = fileURLToPath(import.meta.url);
const executedPath = process.argv[1];

if (scriptPath === executedPath) {
  main();
}