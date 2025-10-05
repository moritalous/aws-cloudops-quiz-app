# Project Structure

## Root Directory
```
vite-project/                 # Main application directory
├── app/                      # React Router v7 app directory
├── public/                   # Static assets
├── scripts/                  # Build and utility scripts
├── node_modules/             # Dependencies
├── package.json              # Project configuration
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript configuration
├── react-router.config.ts   # React Router configuration
└── Dockerfile               # Container configuration
```

## App Directory Structure
```
app/
├── components/              # Reusable UI components
│   ├── QuizScreen.tsx      # Main quiz interface
│   ├── QuestionDisplay.tsx # Question rendering
│   ├── ResultDisplay.tsx   # Answer feedback
│   ├── MenuScreen.tsx      # Mode selection
│   └── LoadingSpinner.tsx  # Loading states
├── hooks/                   # Custom React hooks
│   └── useQuizSession.ts   # Quiz state management
├── routes/                  # Page components (React Router v7)
│   ├── home.tsx            # Landing page
│   ├── quiz.tsx            # Quiz interface
│   └── result.tsx          # Results page
├── types/                   # TypeScript type definitions
│   └── index.ts            # Shared interfaces
├── utils/                   # Business logic utilities
│   ├── data-loader.ts      # Question data loading
│   ├── session-manager.ts  # Session persistence
│   ├── question-selector.ts # Question randomization
│   ├── quiz-manager.ts     # Quiz flow control
│   └── schema-validator.ts # Data validation
├── schemas/                 # JSON schemas
│   └── question-schema.json # Question data validation
├── app.css                  # Global styles (Tailwind)
└── root.tsx                 # App root component
```

## Naming Conventions
- **Components**: PascalCase (e.g., `QuestionDisplay.tsx`)
- **Hooks**: camelCase with `use` prefix (e.g., `useQuizSession.ts`)
- **Utilities**: kebab-case (e.g., `data-loader.ts`)
- **Types**: PascalCase interfaces (e.g., `Question`, `QuizSession`)
- **Routes**: lowercase (e.g., `home.tsx`, `quiz.tsx`)

## File Organization Principles
- **Components** are purely presentational with minimal business logic
- **Hooks** contain stateful logic and side effects
- **Utils** contain pure functions and business logic
- **Types** define shared interfaces across the application
- **Schemas** contain JSON validation schemas
- **Routes** handle page-level concerns and data loading

## Import Patterns
- Use `~/` alias for app directory imports (configured in tsconfig.json)
- Barrel exports from `index.ts` files for clean imports
- Group imports: external libraries, internal modules, relative imports