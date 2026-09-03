import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { casoCreateFormSchema } from '$lib/forms/schemas/caso-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';
import { ApiException } from '$lib/types';
import type { UserOption } from '$lib/types';

export const load: PageLoad = async ({ fetch }) => {
	try {
		const form = await superValidate(zod4(casoCreateFormSchema));
		const usersData = await api.get<{ items: UserOption[] }>('user/opcoes', {}, fetch);
		const usuarios = usersData.items ?? [];

		return { form, usuarios, assistidos: [] };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
