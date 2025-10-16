import { eventoCreateFormSchema } from '$lib/forms/schemas/evento-schema';
import type { Caso } from '$lib/types/caso';
import type { Evento } from '$lib/types/evento';
import type { Paginated } from '$lib/types/paginated';
import { error } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { api } from '$lib/api-client';

export const load = async ({ params, fetch }) => {
	const response = await api.get(`caso/${params.id}`, {}, fetch);

	if (!response.ok) {
		error(404, 'Caso não encontrado');
	}

	const eventosResponse = await api.get(`caso/${params.id}/eventos`, {}, fetch);

	if (!eventosResponse.ok) {
		error(404, 'Eventos não encontrados');
	}

	const eventos: Paginated<Evento> = await eventosResponse.json();

	const caso: Caso = await response.json();

	const eventoFormData = await superValidate(zod4(eventoCreateFormSchema));

	return {
		caso,
		eventos,
		eventoFormData
	};
};
