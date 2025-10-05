import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import type { QuestionSet } from '~/types';

// AJVインスタンスを作成し、フォーマット検証を追加
const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

// スキーマを動的に読み込む
let questionSchema: any = null;
let validateQuestionSet: any = null;

async function loadSchema() {
  if (!questionSchema) {
    const response = await fetch('/schemas/question-schema.json');
    questionSchema = await response.json();
    validateQuestionSet = ajv.compile(questionSchema);
  }
  return validateQuestionSet;
}

export interface ValidationError {
  field: string;
  message: string;
  value?: any;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

/**
 * 問題セットデータをJSONスキーマで検証する
 */
export async function validateQuestionSetData(data: any): Promise<ValidationResult> {
  try {
    const validator = await loadSchema();
    const isValid = validator(data);
    
    if (isValid) {
      return {
        isValid: true,
        errors: []
      };
    }

    const errors: ValidationError[] = [];
    
    if (validator.errors) {
      for (const error of validator.errors) {
        errors.push({
          field: error.instancePath || error.schemaPath,
          message: error.message || 'Validation error',
          value: error.data
        });
      }
    }

    return {
      isValid: false,
      errors
    };
  } catch (error) {
    return {
      isValid: false,
      errors: [{ field: 'schema', message: 'Failed to load schema: ' + (error instanceof Error ? error.message : 'Unknown error') }]
    };
  }
}

/**
 * 個別の問題データを検証する
 */
export async function validateQuestion(question: any): Promise<ValidationResult> {
  try {
    await loadSchema(); // スキーマを読み込み
    
    const questionSchemaDefinition = questionSchema.definitions?.question;
    
    if (!questionSchemaDefinition) {
      return {
        isValid: false,
        errors: [{ field: 'schema', message: 'Question schema definition not found' }]
      };
    }

    const validateSingleQuestion = ajv.compile(questionSchemaDefinition);
    const isValid = validateSingleQuestion(question);

    if (isValid) {
      return {
        isValid: true,
        errors: []
      };
    }

    const errors: ValidationError[] = [];
    
    if (validateSingleQuestion.errors) {
      for (const error of validateSingleQuestion.errors) {
        errors.push({
          field: error.instancePath || error.schemaPath,
          message: error.message || 'Validation error',
          value: error.data
        });
      }
    }

    return {
      isValid: false,
      errors
    };
  } catch (error) {
    return {
      isValid: false,
      errors: [{ field: 'schema', message: 'Failed to validate question: ' + (error instanceof Error ? error.message : 'Unknown error') }]
    };
  }
}

/**
 * 問題データの基本的な整合性をチェック
 */
export function validateQuestionConsistency(data: QuestionSet): ValidationResult {
  const errors: ValidationError[] = [];

  // 問題数の整合性チェック
  if (data.questions.length !== data.totalQuestions) {
    errors.push({
      field: 'totalQuestions',
      message: `Total questions mismatch: expected ${data.totalQuestions}, got ${data.questions.length}`,
      value: data.totalQuestions
    });
  }

  // ドメイン別問題数の整合性チェック
  const domainCounts: { [key: string]: number } = {};
  for (const question of data.questions) {
    domainCounts[question.domain] = (domainCounts[question.domain] || 0) + 1;
  }

  for (const [domain, expectedCount] of Object.entries(data.domains)) {
    const actualCount = domainCounts[domain] || 0;
    if (actualCount !== expectedCount) {
      errors.push({
        field: `domains.${domain}`,
        message: `Domain question count mismatch: expected ${expectedCount}, got ${actualCount}`,
        value: expectedCount
      });
    }
  }

  // 問題IDの重複チェック
  const questionIds = data.questions.map(q => q.id);
  const uniqueIds = new Set(questionIds);
  if (questionIds.length !== uniqueIds.size) {
    errors.push({
      field: 'questions',
      message: 'Duplicate question IDs found',
      value: questionIds
    });
  }

  // 正解の選択肢存在チェック
  for (const question of data.questions) {
    const optionLetters = question.options.map(opt => opt.charAt(0));
    
    if (typeof question.correctAnswer === 'string') {
      if (!optionLetters.includes(question.correctAnswer)) {
        errors.push({
          field: `questions.${question.id}.correctAnswer`,
          message: `Correct answer '${question.correctAnswer}' not found in options`,
          value: question.correctAnswer
        });
      }
    } else if (Array.isArray(question.correctAnswer)) {
      for (const answer of question.correctAnswer) {
        if (!optionLetters.includes(answer)) {
          errors.push({
            field: `questions.${question.id}.correctAnswer`,
            message: `Correct answer '${answer}' not found in options`,
            value: answer
          });
        }
      }
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * 学習リソースURLの有効性をチェック（基本的な形式チェック）
 */
export function validateLearningResourceUrls(data: QuestionSet): ValidationResult {
  const errors: ValidationError[] = [];
  const urlPattern = /^https?:\/\/.+/;

  for (const question of data.questions) {
    for (const resource of question.learningResources) {
      if (!urlPattern.test(resource.url)) {
        errors.push({
          field: `questions.${question.id}.learningResources`,
          message: `Invalid URL format: ${resource.url}`,
          value: resource.url
        });
      }
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * 包括的な問題セット検証
 */
export async function validateQuestionSetComprehensive(data: any): Promise<ValidationResult> {
  // 1. JSONスキーマ検証
  const schemaResult = await validateQuestionSetData(data);
  if (!schemaResult.isValid) {
    return schemaResult;
  }

  // 2. データ整合性検証
  const consistencyResult = validateQuestionConsistency(data as QuestionSet);
  if (!consistencyResult.isValid) {
    return consistencyResult;
  }

  // 3. URL検証
  const urlResult = validateLearningResourceUrls(data as QuestionSet);
  if (!urlResult.isValid) {
    return urlResult;
  }

  return {
    isValid: true,
    errors: []
  };
}