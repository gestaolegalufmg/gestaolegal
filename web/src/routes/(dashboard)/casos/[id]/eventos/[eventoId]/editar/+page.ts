import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { eventoUpdateFormSchema } from '$lib/forms/schemas/evento-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';

export const load: PageLoad = async ({ params, fetch }) => {
	const eventoResponse = await api.get(`caso/${params.id}/eventos/${params.eventoId}`, {}, fetch);

	if (!eventoResponse.ok) {
		error(eventoResponse.status, 'Evento nao encontrado');
	}

	const evento = await eventoResponse.json();

	const form = await superValidate(
		{
			tipo: evento.tipo,
			descricao: evento.descricao ?? '',
			data_evento: evento.data_evento,
			id_usuario_responsavel: evento.id_usuario_responsavel ?? null,
			status: evento.status,
			arquivo: null
		},
		zod4(eventoUpdateFormSchema)
	);

	return {
		evento,
		form
	};
};
