import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	const response = await fetch(`/api/atendido/${params.id}`);

	if (!response.ok) {
		error(response.status, 'Atendido não encontrado');
	}

	const atendido = await response.json();

	return { atendido };
};
