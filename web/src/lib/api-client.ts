import { dev } from '$app/environment';
import { env } from '$env/dynamic/public';

function getAuthToken(): string | null {
	if (typeof document === 'undefined') return null;

	const cookie = document.cookie.split('; ').find((row) => row.startsWith('auth_token='));

	return cookie ? cookie.split('=')[1] : null;
}

const isNonEmpty = (value: string | undefined | null) =>
	value !== undefined && value !== null && value.trim().length > 0;

const resolveConfiguredApiUrl = () => {
	const configured = env.PUBLIC_API_URL;
	return isNonEmpty(configured) ? configured!.trim() : null;
};

const getApiBaseUrl = () => {
	const configuredUrl = resolveConfiguredApiUrl();

	if (dev) {
		console.log('Using configured API URL:', configuredUrl);
		return `${configuredUrl}/api`;
	}

	console.log('Using same origin API URL and delegating nginx to proxy requests');
	return '/api';
};

export async function apiFetch(
	endpoint: string,
	options: RequestInit = {},
	customFetch: typeof fetch = fetch
): Promise<Response> {
	const token = getAuthToken();
	const baseUrl = getApiBaseUrl();

	const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;

	const url = `${baseUrl}/${cleanEndpoint}`;

	const headers = new Headers(options.headers || {});

	if (token) {
		headers.set('Authorization', `Bearer ${token}`);
	}

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
		credentials: 'include'
	});

	if (response.status === 401) {
		if (typeof document !== 'undefined') {
			document.cookie = 'auth_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
		}

		if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
			window.location.href = '/login';
		}
	}

	return response;
}

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
