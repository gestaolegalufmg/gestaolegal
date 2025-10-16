import type { OrientacaoJuridica, Paginated } from '$lib/types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { superValidate } from 'sveltekit-superforms/client';
import { z } from 'zod/v4';

const orientacaoSearchSchema = z.object({
	search: z.string().optional().default(''),
	show_inactive: z.boolean().optional().default(false),
	area: z.string().optional().default('todas')
});

export const load = async ({ fetch, depends, url }) => {
	depends('app:orientacoes-juridicas');

	const urlParams = url.searchParams;
	const response = await fetch(`/api/orientacao_juridica?${urlParams.toString()}`);

	const data: Paginated<OrientacaoJuridica> = await response.json();

	const formData = await superValidate(
		{
			search: urlParams.get('search') || '',
			show_inactive: urlParams.get('show_inactive') === 'true',
			area: urlParams.get('area') || 'todas'
		},
		zod4(orientacaoSearchSchema)
	);
	return {
		orientacoes: data,
		formData
	};
};
