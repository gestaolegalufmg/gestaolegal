import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';

export const load: PageLoad = async ({ params, fetch }) => {
	const eventoResponse = await api.get(`caso/${params.id}/eventos/${params.eventoId}`, {}, fetch);

	if (!eventoResponse.ok) {
		error(eventoResponse.status, 'Evento nao encontrado');
	}

	const evento = await eventoResponse.json();

	return { evento };
};
