import type { OrientacaoJuridica, Paginated } from '$lib/types';
import { orientacaoSearchSchema } from '$lib/forms/schemas/orientacao-juridica-schema';
import { zod4 } from 'sveltekit-superforms/adapters';
import { superValidate } from 'sveltekit-superforms/client';
import { api } from '$lib/api-client';

export const load = async ({ depends, url, fetch }) => {
	depends('app:orientacoes-juridicas');

	const urlParams = url.searchParams;
	const response = await api.get(`orientacao_juridica?${urlParams.toString()}`, {}, fetch);

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
