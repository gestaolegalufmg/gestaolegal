import type { ListCaso, Paginated } from '$lib/types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { superValidate } from 'sveltekit-superforms/client';
import { z } from 'zod/v4';

const casoSearchSchema = z.object({
	search: z.string().optional().default(''),
	show_inactive: z.boolean().optional().default(false),
	situacao_deferimento: z.string().optional().default('todos')
});

export const load = async ({ fetch, depends, url }) => {
	depends('app:casos');

	const urlParams = url.searchParams;
	const response = await fetch(`/api/caso?${urlParams.toString()}`);

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
