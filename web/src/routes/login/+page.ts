import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { loginSchema } from '$lib/forms/schemas/login-schema';
import { api } from '$lib/api-client';
import { ApiException } from '$lib/types';

export const load = async ({ fetch }) => {
	const form = await superValidate(zod4(loginSchema));

	try {
		// New API: returns unwrapped data directly with type safety
		const data = await api.get<{ needs_setup: boolean }>('auth/needs-setup', {}, fetch);

		return {
			form,
			needsSetup: data.needs_setup
		};
	} catch (error) {
		// Handle API errors gracefully
		if (error instanceof ApiException) {
			console.error('API error checking setup status:', error.message);
		} else {
			console.error('Failed to check setup status:', error);
		}

		// Default to false on error - user can still try to login
		return {
			form,
			needsSetup: false
		};
	}
};
