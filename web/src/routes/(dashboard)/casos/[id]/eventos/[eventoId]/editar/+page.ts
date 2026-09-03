import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { eventoUpdateFormSchema } from '$lib/forms/schemas/evento-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';
import { ApiException } from '$lib/types';
import type { Evento } from '$lib/types/evento';
import { toISODateInput } from '$lib/utils/date';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const evento = await api.get<Evento>(`caso/${params.id}/eventos/${params.eventoId}`, {}, fetch);

		const form = await superValidate(
			{
				tipo: evento.tipo,
				descricao: evento.descricao ?? '',
				// API sends dates as GMT strings; the picker/schema need ISO YYYY-MM-DD.
				data_evento: toISODateInput(evento.data_evento),
				id_usuario_responsavel: evento.id_usuario_responsavel ?? null,
				status: evento.status,
				arquivo: null
			},
			zod4(eventoUpdateFormSchema),
			{ id: 'evento-edit-form' }
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
