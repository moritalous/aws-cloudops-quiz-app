import type { Config } from '@react-router/dev/config';

export default {
  // Config options...
  // Server-side render by default, to enable SPA mode set this to `false`
  ssr: false,
  // GitHub Pages用のbasename設定
  basename: process.env.NODE_ENV === 'production' ? '/aws-cloudops-quiz-app' : undefined,
} satisfies Config;
