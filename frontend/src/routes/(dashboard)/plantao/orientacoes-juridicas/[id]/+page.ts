import { error } from '@sveltejs/kit';
import type { OrientacaoJuridica } from '$lib/types';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	const response = await fetch(`/api/orientacao_juridica/${params.id}`);

	if (!response.ok) {
		error(response.status, 'Orientação Jurídica não encontrada');
	}

	const orientacao = (await response.json()) as OrientacaoJuridica;

	return { orientacao };
};
