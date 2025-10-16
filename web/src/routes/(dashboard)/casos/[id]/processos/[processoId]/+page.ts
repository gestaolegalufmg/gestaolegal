import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';

export const load: PageLoad = async ({ params, fetch }) => {
	const response = await api.get(`caso/${params.id}/processos/${params.processoId}`, {}, fetch);

	if (!response.ok) {
		error(404, 'Processo não encontrado');
	}

	const processo = await response.json();

	return { processo };
};
