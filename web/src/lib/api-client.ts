/**
 * API Client for SPA mode
 * Handles authentication and base URL configuration
 */

// Helper to get auth token from cookie
function getAuthToken(): string | null {
	if (typeof document === 'undefined') return null;

	const cookie = document.cookie.split('; ').find((row) => row.startsWith('auth_token='));

	return cookie ? cookie.split('=')[1] : null;
}

// Get API base URL - use proxy in dev, direct in production
const getApiBaseUrl = () => {
	// In SPA mode, we can call the backend directly
	// or use nginx reverse proxy in production
	if (typeof window !== 'undefined') {
		// Check if we're using a proxy (same origin)
		return '/api'; // nginx will proxy this to backend
	}
	return '/api';
};

/**
 * Enhanced fetch that automatically adds authentication
 * @param endpoint - API endpoint (without /api prefix)
 * @param options - Fetch options
 * @param customFetch - Optional fetch function (use event.fetch in load functions)
 */
export async function apiFetch(
	endpoint: string,
	options: RequestInit = {},
	customFetch: typeof fetch = fetch
): Promise<Response> {
	const token = getAuthToken();
	const baseUrl = getApiBaseUrl();

	// Remove leading slash from endpoint if present
	const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;

	const url = `${baseUrl}/${cleanEndpoint}`;

	const headers = new Headers(options.headers || {});

	// Add auth token if available
	if (token) {
		headers.set('Authorization', `Bearer ${token}`);
	}

	// Add Content-Type for JSON requests if not already set
	// Don't set Content-Type for FormData, browser will set it automatically with boundary
	if (
		options.body &&
		typeof options.body === 'string' &&
		!headers.has('Content-Type') &&
		!(options.body instanceof FormData)
	) {
		headers.set('Content-Type', 'application/json');
	}

	const response = await customFetch(url, {
		...options,
		headers,
		credentials: 'include' // Include cookies
	});

	// Handle 401 - redirect to login
	if (response.status === 401) {
		// Clear auth cookie
		document.cookie = 'auth_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';

		// Redirect to login if not already there
		if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
			window.location.href = '/login';
		}
	}

	return response;
}

/**
 * API helper methods
 * In load functions, pass the fetch parameter: api.get('endpoint', {}, fetch)
 */
export const api = {
	get: (endpoint: string, options?: RequestInit, customFetch?: typeof fetch) =>
		apiFetch(endpoint, { ...options, method: 'GET' }, customFetch),

	post: (endpoint: string, data?: any, options?: RequestInit, customFetch?: typeof fetch) =>
		apiFetch(
			endpoint,
			{
				...options,
				method: 'POST',
				body: data instanceof FormData ? data : data ? JSON.stringify(data) : undefined
			},
			customFetch
		),

	put: (endpoint: string, data?: any, options?: RequestInit, customFetch?: typeof fetch) =>
		apiFetch(
			endpoint,
			{
				...options,
				method: 'PUT',
				body: data ? JSON.stringify(data) : undefined
			},
			customFetch
		),

	patch: (endpoint: string, data?: any, options?: RequestInit, customFetch?: typeof fetch) =>
		apiFetch(
			endpoint,
			{
				...options,
				method: 'PATCH',
				body: data ? JSON.stringify(data) : undefined
			},
			customFetch
		),

	delete: (endpoint: string, options?: RequestInit, customFetch?: typeof fetch) =>
		apiFetch(endpoint, { ...options, method: 'DELETE' }, customFetch)
};
