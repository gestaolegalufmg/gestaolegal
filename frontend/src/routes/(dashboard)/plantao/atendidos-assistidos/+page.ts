import type { ListAtendido, Paginated } from '$lib/types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { superValidate } from 'sveltekit-superforms/client';
import { z } from 'zod/v4';

const atendidoSearchSchema = z.object({
	search: z.string().optional().default(''),
	show_inactive: z.boolean().optional().default(false),
	tipo_busca: z.string().optional().default('todos')
});

export const load = async ({ fetch, depends, url }) => {
	depends('app:atendidos');

	const urlParams = url.searchParams;
	const response = await fetch(`/api/atendido?${urlParams.toString()}`);

	const data: Paginated<ListAtendido> = await response.json();

	const formData = await superValidate(
		{
			search: urlParams.get('search') || '',
			show_inactive: urlParams.get('show_inactive') === 'true',
			tipo_busca: urlParams.get('tipo_busca') || 'todos'
		},
		zod4(atendidoSearchSchema)
	);
	return {
		atendidos: data,
		formData
	};
};
