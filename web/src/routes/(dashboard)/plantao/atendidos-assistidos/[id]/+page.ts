import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';

export const load: PageLoad = async ({ params, fetch }) => {
	const response = await api.get(`atendido/${params.id}`, {}, fetch);

	if (!response.ok) {
		error(response.status, 'Atendido não encontrado');
	}

	const atendido = await response.json();

	return { atendido };
};
