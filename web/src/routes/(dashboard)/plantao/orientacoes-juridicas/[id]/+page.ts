import { error } from '@sveltejs/kit';
import type { OrientacaoJuridica } from '$lib/types';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';

export const load: PageLoad = async ({ params, fetch }) => {
	const response = await api.get(`orientacao_juridica/${params.id}`, {}, fetch);

	if (!response.ok) {
		error(response.status, 'Orientação Jurídica não encontrada');
	}

	const orientacao = (await response.json()) as OrientacaoJuridica;

	return { orientacao };
};
