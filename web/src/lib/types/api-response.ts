/**
 * Standard API response wrapper returned by all backend endpoints.
 *
 * The backend wraps all responses in this structure for consistency:
 * - Success responses have success=true and data
 * - Error responses have success=false and error details
 */
export interface ApiResponse<T> {
	/** Whether the request was successful */
	success: boolean;

	/** Response data (only present on success) */
	data?: T;

	/** Error details (only present on failure) */
	error?: ApiError;

	/** Optional message (success or error description) */
	message?: string;

	/** Optional metadata (e.g., timestamp) */
	metadata?: {
		timestamp?: string;
	};
}

/**
 * Error structure returned by the backend when a request fails.
 */
export interface ApiError {
	/** Human-readable error message */
	message: string;

	/** Machine-readable error code for programmatic handling */
	code?: string;

	/** Additional error details (e.g., validation errors, field names) */
	details?: any;
}

/**
 * Exception thrown when an API request fails.
 *
 * This provides a consistent way to handle API errors throughout the application.
 * The error includes both the user-facing message and technical details for debugging.
 *
 * @example
 * ```typescript
 * try {
 *   const data = await api.get<User>('user/123');
 * } catch (err) {
 *   if (err instanceof ApiException) {
 *     toast.error(err.message); // Show user-friendly message
 *     console.error(err.code, err.details); // Log technical details
 *   }
 * }
 * ```
 */
export class ApiException extends Error {
	constructor(
		message: string,
		public code?: string,
		public details?: any,
		public statusCode?: number
	) {
		super(message);
		this.name = 'ApiException';

		// Maintains proper stack trace for where our error was thrown (only available on V8)
		if (Error.captureStackTrace) {
			Error.captureStackTrace(this, ApiException);
		}
	}
}
