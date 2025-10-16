import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { casoCreateFormSchema } from '$lib/forms/schemas/caso-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';

export const load: PageLoad = async ({ fetch }) => {
	const form = await superValidate(zod4(casoCreateFormSchema));

	const usersResponse = await api.get('user?per_page=1000', {}, fetch);

	if (!usersResponse.ok) {
		error(usersResponse.status, 'Nao foi possivel carregar usuarios');
	}

	const usersData = await usersResponse.json();
	const usuarios = usersData.items ?? [];

	return { form, usuarios, assistidos: [] };
};
