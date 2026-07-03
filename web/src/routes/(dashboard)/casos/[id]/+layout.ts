import { eventoCreateFormSchema } from '$lib/forms/schemas/evento-schema';
import type { Caso } from '$lib/types/caso';
import type { Evento } from '$lib/types/evento';
import type { Paginated } from '$lib/types/paginated';
import type { Historico, Lembrete } from '$lib/types';
import { error } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { api } from '$lib/api-client';
import { ApiException } from '$lib/types';

export const load = async ({ params, fetch }) => {
	try {
		const [caso, eventos, lembretes, historico] = await Promise.all([
			api.get<Caso>(`caso/${params.id}`, {}, fetch),
			api.get<Paginated<Evento>>(`caso/${params.id}/eventos`, {}, fetch),
			api.get<Lembrete[]>(`caso/${params.id}/lembretes`, {}, fetch),
			api.get<Paginated<Historico>>(`caso/${params.id}/historico`, {}, fetch)
		]);

		const eventoFormData = await superValidate(zod4(eventoCreateFormSchema));

		return {
			caso,
			eventos,
			lembretes,
			historico,
			eventoFormData
		};
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 404, err.message);
		}
		throw err;
	}
};
