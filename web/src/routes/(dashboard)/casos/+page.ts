import type { ListCaso, Paginated } from '$lib/types';
import { casoSearchSchema } from '$lib/forms/schemas/caso-schema';
import { zod4 } from 'sveltekit-superforms/adapters';
import { superValidate } from 'sveltekit-superforms/client';
import { api } from '$lib/api-client';

export const load = async ({ depends, url, fetch }) => {
	depends('app:casos');

	const urlParams = url.searchParams;
	const response = await api.get(`caso?${urlParams.toString()}`, {}, fetch);

	const data: Paginated<ListCaso> = await response.json();

	const formData = await superValidate(
		{
			search: urlParams.get('search') || '',
			show_inactive: urlParams.get('show_inactive') === 'true',
			situacao_deferimento: urlParams.get('situacao_deferimento') || 'todos'
		},
		zod4(casoSearchSchema)
	);
	return {
		casos: data,
		formData
	};
};
