import { type Handle } from '@sveltejs/kit';

/**
 * Server hooks for SPA mode
 * NOTE: With adapter-static, these hooks only run during BUILD time
 * At runtime, the app is pure static files served by nginx
 * Authentication is handled client-side in +layout.svelte
 */

export const handle: Handle = async ({ event, resolve }) => {
	// No server-side redirects in SPA mode
	// Auth is handled client-side
	return await resolve(event);
};

export const handleError = async ({ status, message, error: requestError }) => {
	console.error('Build-time error occurred:', {
		status,
		message,
		error: (requestError as any)?.message || requestError,
		stack: (requestError as any)?.stack
	});

	// Return error details for build process
	return {
		message: message || 'Ocorreu um erro inesperado',
		status
	};
};
