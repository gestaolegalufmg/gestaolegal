import { eventoCreateFormSchema } from '$lib/forms/schemas/evento-schema';
import type { Caso } from '$lib/types/caso';
import type { Evento } from '$lib/types/evento';
import type { Paginated } from '$lib/types/paginated';
import { error } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';

export const load = async ({ params, fetch }) => {
	const response = await fetch(`/api/caso/${params.id}`);

	if (!response.ok) {
		error(404, 'Caso não encontrado');
	}

	const eventosResponse = await fetch(`/api/caso/${params.id}/eventos`);

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
