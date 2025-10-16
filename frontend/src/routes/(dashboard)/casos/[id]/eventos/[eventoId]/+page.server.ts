import { error } from '@sveltejs/kit';
import type { Evento } from '$lib/types/evento';

export const load = async ({ params, fetch, parent }) => {
	const eventoResponse = await fetch(`/api/caso/${params.id}/eventos/${params.eventoId}`);

	if (!eventoResponse.ok) {
		error(404, 'Evento não encontrado');
	}

	const evento: Evento = await eventoResponse.json();

	return {
		evento
	};
};
