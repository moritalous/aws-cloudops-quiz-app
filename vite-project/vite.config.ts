import { reactRouter } from '@react-router/dev/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig(({ mode }) => {
  // GitHub Pages用のbase path設定
  // 本番環境（GitHub Pages）では'aws-cloudops-quiz-app'リポジトリ名を使用
  // ローカル環境では'/'を使用
  const base = mode === 'production'
    ? '/aws-cloudops-quiz-app/'
    : '/';

  return {
    base,
    plugins: [tailwindcss(), reactRouter(), tsconfigPaths()],
    assetsInclude: ['**/*.json'],
  };
});
