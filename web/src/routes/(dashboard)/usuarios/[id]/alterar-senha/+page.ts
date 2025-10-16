import { passwordChangeSchema } from '$lib/forms/schemas/password-schema';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';

export const load: PageLoad = async ({ params, fetch }) => {
	const userId = params.id;

	const userResponse = await api.get(`user/${userId}`, {}, fetch);

	if (!userResponse.ok) {
		throw new Error('Usuário não encontrado');
	}

	const user = await userResponse.json();
	const form = await superValidate(zod4(passwordChangeSchema));

	return {
		user,
		form
	};
};
