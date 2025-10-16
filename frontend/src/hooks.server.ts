import { error, redirect, type Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
	const { cookies, url } = event;

	const auth_token = cookies.get('auth_token');

	if (auth_token) {
		event.locals.auth_token = auth_token;
	}

	const isPublicRoute =
		url.pathname === '/login' ||
		url.pathname.startsWith('/api/') ||
		url.pathname.startsWith('/_app/');

	if (!isPublicRoute && !auth_token) {
		redirect(302, '/login');
	}

	return await resolve(event);
};

export const handleFetch = async ({ event, request, fetch }) => {
	const auth_token = event.locals.auth_token;
	if (auth_token) {
		request.headers.set('Authorization', `Bearer ${auth_token}`);
	}

	const response = await fetch(request, {
		credentials: 'include'
	});

	return response;
};

export const handleError = async ({ event, status, message, error: requestError }) => {
	console.error('Error occurred:', {
		url: event?.url?.href,
		method: event?.request?.method,
		status,
		message,
		error: (requestError as any)?.message || requestError,
		stack: (requestError as any)?.stack
	});

	if (status === 404) {
		error(404, 'Página não encontrada');
	}

	if (status === 401) {
		error(401, 'Não autorizado. Faça login novamente.');
	}

	if (status === 403) {
		error(403, 'Acesso negado. Você não tem permissão para acessar este recurso.');
	}

	if (status >= 500) {
		error(500, 'Erro interno do servidor. Tente novamente mais tarde.');
	}

	error(status, message || 'Ocorreu um erro inesperado');
};
