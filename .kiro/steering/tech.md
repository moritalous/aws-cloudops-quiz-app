# Technology Stack

## Frontend Framework
- **React 19** with TypeScript
- **React Router v7** for routing and SSR
- **Tailwind CSS v4** for styling
- **Vite** as build tool and dev server

## Development Tools
- **TypeScript** for type safety
- **ESLint** for code linting
- **Prettier** for code formatting
- **Vitest** for unit testing
- **React Testing Library** for component testing

## Build System
- **Vite** with React Router plugin
- **Node.js** ES modules (type: "module")
- **TypeScript** compilation with strict mode
- **Tailwind CSS** with Vite plugin integration

## Key Dependencies
- `@react-router/node` and `@react-router/serve` for SSR
- `ajv` and `ajv-formats` for JSON schema validation
- `isbot` for bot detection

## Common Commands

```bash
# Development
npm run dev              # Start development server
npm run typecheck        # Type checking with React Router typegen

# Testing
npm run test             # Run tests once
npm run test:watch       # Run tests in watch mode
npm run test:ui          # Run tests with UI

# Code Quality
npm run lint             # Run ESLint
npm run lint:fix         # Fix ESLint issues
npm run format           # Format code with Prettier

# Build & Deploy
npm run build            # Production build
npm run start            # Start production server

# Custom Scripts
npm run validate:questions  # Validate question data format
```

## Architecture Patterns
- **Component-based architecture** with reusable UI components
- **Custom hooks** for state management and business logic
- **Utility classes** for data processing and validation
- **JSON schema validation** for data integrity
- **Session storage** for persistence without backend