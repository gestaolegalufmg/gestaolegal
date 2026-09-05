import { dev } from '$app/environment';
import { env } from '$env/dynamic/public';
import { ApiException, type ApiResponse } from './types/api-response';
import { unidadeAtivaId } from './stores/unidade';

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

	// A API exige a unidade ativa em quase toda rota; as poucas que não exigem
	// (auth/*, user/me, user/opcoes, unidades do seletor) ignoram o header.
	const unidadeId = unidadeAtivaId();

	if (unidadeId !== null) {
		headers.set('X-Unidade-Id', String(unidadeId));
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

async function unwrapApiResponse<T>(response: Response): Promise<T> {
	let apiResponse: ApiResponse<T>;
	try {
		apiResponse = await response.json();
	} catch {
		throw new ApiException(
			response.status === 403
				? 'Você não tem permissão para executar esta ação. Contate o administrador.'
				: 'Erro na requisição',
			undefined,
			undefined,
			response.status
		);
	}

	if (!apiResponse.success) {
		throw new ApiException(
			apiResponse.error?.message || 'Erro na requisição',
			apiResponse.error?.code,
			apiResponse.error?.details,
			response.status
		);
	}

	return apiResponse.data as T;
}

async function apiData<T>(
	endpoint: string,
	options?: RequestInit,
	customFetch?: typeof fetch
): Promise<T> {
	const response = await apiFetch(endpoint, options, customFetch);
	return unwrapApiResponse<T>(response);
}

export const api = {
	get: <T>(endpoint: string, options?: RequestInit, customFetch?: typeof fetch) =>
		apiData<T>(endpoint, { ...options, method: 'GET' }, customFetch),

	post: <T>(endpoint: string, data?: any, options?: RequestInit, customFetch?: typeof fetch) =>
		apiData<T>(
			endpoint,
			{
				...options,
				method: 'POST',
				body: data instanceof FormData ? data : data ? JSON.stringify(data) : undefined
			},
			customFetch
		),

	put: <T>(endpoint: string, data?: any, options?: RequestInit, customFetch?: typeof fetch) =>
		apiData<T>(
			endpoint,
			{
				...options,
				method: 'PUT',
				body: data instanceof FormData ? data : data ? JSON.stringify(data) : undefined
			},
			customFetch
		),

	patch: <T>(endpoint: string, data?: any, options?: RequestInit, customFetch?: typeof fetch) =>
		apiData<T>(
			endpoint,
			{
				...options,
				method: 'PATCH',
				body: data instanceof FormData ? data : data ? JSON.stringify(data) : undefined
			},
			customFetch
		),

	delete: <T = void>(endpoint: string, options?: RequestInit, customFetch?: typeof fetch) =>
		apiData<T>(endpoint, { ...options, method: 'DELETE' }, customFetch)
};
