"""
Error handling and retry logic for the question generation system.

This module provides comprehensive error handling, custom exceptions,
and retry mechanisms for robust operation of the AI-driven system.
"""

import time
import logging
from typing import Callable, Any, Optional, Type, Union
from functools import wraps
import random

logger = logging.getLogger(__name__)


class QuestionGenerationError(Exception):
    """Base exception for question generation system."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class BedrockConnectionError(QuestionGenerationError):
    """Exception raised when Bedrock connection fails."""
    pass


class MCPConnectionError(QuestionGenerationError):
    """Exception raised when MCP connection fails."""
    pass


class ValidationError(QuestionGenerationError):
    """Exception raised when validation fails."""
    pass


class RetryableError(QuestionGenerationError):
    """Exception that indicates the operation can be retried."""
    pass


class NonRetryableError(QuestionGenerationError):
    """Exception that indicates the operation should not be retried."""
    pass


class ExamGuideAnalysisError(QuestionGenerationError):
    """Exception raised when exam guide analysis fails."""
    pass


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is retryable.
    
    Args:
        error: The exception to check
    
    Returns:
        True if the error is retryable, False otherwise
    """
    # Explicitly retryable errors
    if isinstance(error, RetryableError):
        return True
    
    # Explicitly non-retryable errors
    if isinstance(error, NonRetryableError):
        return False
    
    # Connection errors are generally retryable
    if isinstance(error, (BedrockConnectionError, MCPConnectionError)):
        return True
    
    # Check for common retryable error patterns
    error_message = str(error).lower()
    retryable_patterns = [
        'timeout',
        'connection',
        'network',
        'throttling',
        'rate limit',
        'service unavailable',
        'internal server error',
        'temporary failure',
        'try again',
    ]
    
    for pattern in retryable_patterns:
        if pattern in error_message:
            return True
    
    # Validation errors are generally not retryable
    if isinstance(error, ValidationError):
        return False
    
    # Default to non-retryable for unknown errors
    return False


def calculate_backoff_delay(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> float:
    """
    Calculate backoff delay for retry attempts.
    
    Args:
        attempt: Current attempt number (0-based)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
    
    Returns:
        Delay in seconds
    """
    # Calculate exponential backoff
    delay = base_delay * (exponential_base ** attempt)
    
    # Cap at maximum delay
    delay = min(delay, max_delay)
    
    # Add jitter to avoid thundering herd
    if jitter:
        jitter_amount = delay * 0.1  # 10% jitter
        delay += random.uniform(-jitter_amount, jitter_amount)
    
    return max(0, delay)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Optional[tuple] = None
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delays
        retryable_exceptions: Tuple of exception types to retry on
    
    Returns:
        Decorated function with retry logic
    """
    if retryable_exceptions is None:
        retryable_exceptions = (RetryableError, BedrockConnectionError, MCPConnectionError)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    # Check if this is the last attempt
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries + 1} attempts. "
                            f"Final error: {e}"
                        )
                        raise
                    
                    # Check if error is retryable
                    if not (isinstance(e, retryable_exceptions) or is_retryable_error(e)):
                        logger.error(
                            f"Function {func.__name__} failed with non-retryable error: {e}"
                        )
                        raise
                    
                    # Calculate delay and wait
                    delay = calculate_backoff_delay(
                        attempt, base_delay, max_delay, exponential_base, jitter
                    )
                    
                    logger.warning(
                        f"Function {func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}. "
                        f"Error: {e}. Retrying in {delay:.2f} seconds..."
                    )
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handling for the question generation system."""
    
    def __init__(self, enable_graceful_degradation: bool = True):
        """
        Initialize error handler.
        
        Args:
            enable_graceful_degradation: Whether to enable graceful degradation
        """
        self.enable_graceful_degradation = enable_graceful_degradation
        self.error_counts = {}
        self.error_history = []
    
    def handle_error(
        self,
        error: Exception,
        context: str,
        operation: str,
        critical: bool = False
    ) -> bool:
        """
        Handle an error with appropriate logging and decision making.
        
        Args:
            error: The exception that occurred
            context: Context where the error occurred
            operation: The operation that failed
            critical: Whether this is a critical error
        
        Returns:
            True if operation should continue, False if it should stop
        """
        error_key = f"{context}:{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        error_info = {
            'error': str(error),
            'type': type(error).__name__,
            'context': context,
            'operation': operation,
            'critical': critical,
            'count': self.error_counts[error_key],
            'timestamp': time.time()
        }
        
        self.error_history.append(error_info)
        
        # Log the error
        log_message = f"Error in {context} during {operation}: {error}"
        if critical:
            logger.critical(log_message)
        else:
            logger.error(log_message)
        
        # Decide whether to continue
        if critical:
            return False
        
        if not self.enable_graceful_degradation:
            return False
        
        # Check if we've seen too many of this error type
        if self.error_counts[error_key] > 5:
            logger.error(f"Too many errors of type {error_key}, stopping operation")
            return False
        
        # For retryable errors, suggest continuation
        if is_retryable_error(error):
            logger.info(f"Error is retryable, suggesting continuation")
            return True
        
        # For validation errors, continue but log warning
        if isinstance(error, ValidationError):
            logger.warning(f"Validation error encountered, continuing with degraded quality")
            return True
        
        # Default to stopping for unknown errors
        return False
    
    def get_error_summary(self) -> dict:
        """Get a summary of all errors encountered."""
        return {
            'total_errors': len(self.error_history),
            'error_counts': self.error_counts.copy(),
            'recent_errors': self.error_history[-10:] if self.error_history else [],
            'critical_errors': [e for e in self.error_history if e['critical']],
            'most_common_errors': sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def reset_error_tracking(self):
        """Reset error tracking counters."""
        self.error_counts.clear()
        self.error_history.clear()
        logger.info("Error tracking reset")


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_error(
    error: Exception,
    context: str,
    operation: str,
    critical: bool = False
) -> bool:
    """
    Convenience function for handling errors.
    
    Args:
        error: The exception that occurred
        context: Context where the error occurred
        operation: The operation that failed
        critical: Whether this is a critical error
    
    Returns:
        True if operation should continue, False if it should stop
    """
    return get_error_handler().handle_error(error, context, operation, critical)