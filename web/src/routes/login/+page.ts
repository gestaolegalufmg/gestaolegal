import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { loginSchema } from '$lib/forms/schemas/login-schema';
import { apiFetch } from '$lib/api-client';

export const load = async ({ fetch }) => {
	const form = await superValidate(zod4(loginSchema));

	let needsSetup = false;
	try {
		const response = await apiFetch('auth/needs-setup', { method: 'GET' }, fetch);
		if (response.ok) {
			const data = await response.json();
			needsSetup = data.needs_setup;
		}
	} catch (error) {
		console.error('Failed to check setup status:', error);
	}

	return { form, needsSetup };
};
