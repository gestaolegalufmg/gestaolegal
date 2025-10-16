import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
	const response = await fetch(`/api/caso/${params.id}/processos/${params.processoId}`);

	if (!response.ok) {
		error(404, 'Processo não encontrado');
	}

	const processo = await response.json();

	return { processo };
};
