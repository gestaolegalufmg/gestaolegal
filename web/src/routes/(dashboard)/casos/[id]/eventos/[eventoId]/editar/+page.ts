import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { eventoUpdateFormSchema } from '$lib/forms/schemas/evento-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';
import { ApiException } from '$lib/types';
import type { Evento } from '$lib/types/evento';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const evento = await api.get<Evento>(`caso/${params.id}/eventos/${params.eventoId}`, {}, fetch);

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
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
