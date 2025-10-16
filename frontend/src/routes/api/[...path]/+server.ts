import { env } from '$env/dynamic/private';
import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const handler: RequestHandler = async ({ params, url, request, fetch }) => {
	try {
		const backendUrl = `${env.GESTAOLEGAL_API_URL}/api/${params.path}${url.search || ''}`;

		const headers = new Headers(request.headers);

		const options: RequestInit = {
			method: request.method,
			headers
		};

		if (['POST', 'PUT', 'PATCH'].includes(request.method)) {
			options.body = request.body;

			// @ts-ignore
			options.duplex = 'half';
		}

		const response = await fetch(backendUrl, options);

		return response;
	} catch (err) {
		console.error('API proxy error:', err);
		error(500, 'Erro ao comunicar com o servidor');
	}
};

export const GET: RequestHandler = handler;
export const POST: RequestHandler = handler;
export const PUT: RequestHandler = handler;
export const PATCH: RequestHandler = handler;
export const DELETE: RequestHandler = handler;
