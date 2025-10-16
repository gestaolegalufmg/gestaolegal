import { superValidate } from 'sveltekit-superforms';
import { loginSchema } from '$lib/forms/schemas/login-schema';
import { zod4 } from 'sveltekit-superforms/adapters';
import type { Actions, PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ cookies }) => {
	const form = await superValidate(zod4(loginSchema));

	if (cookies.get('auth_token')) {
		cookies.delete('auth_token', { path: '/' });
	}

	return { form };
};

export const actions: Actions = {
	login: async (event) => {
		const { fetch, request, url } = event;

		const form = await superValidate(request, zod4(loginSchema));

		if (!form.valid) {
			return { form };
		}

		const response = await fetch(`/api/auth/login`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(form.data)
		});

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			return {
				form: {
					...form,
					errors: {
						_errors: [errorData.message || 'Credenciais inválidas']
					}
				}
			};
		}

		const data = await response.json();

		event.cookies.set('auth_token', data.token, {
			path: '/',
			httpOnly: true,
			secure: true,
			sameSite: 'strict'
		});

		const redirectTo = url.searchParams.get('redirectTo') || '/';
		redirect(302, redirectTo);
	},

	logout: async (event) => {
		event.cookies.delete('auth_token', {
			path: '/'
		});

		return redirect(302, '/login');
	}
};
