import { superValidate } from 'sveltekit-superforms';
import { error } from '@sveltejs/kit';
import { zod4 } from 'sveltekit-superforms/adapters';
import { atendidoUpdateFormSchema } from '$lib/forms/schemas/atendido-schema';
import { assistidoUpdateFormSchema } from '$lib/forms/schemas/assistido-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';

export const load: PageLoad = async ({ params, fetch }) => {
	const response = await api.get(`atendido/${params.id}`, {}, fetch);

	if (!response.ok) {
		error(response.status);
	}

	const atendido = await response.json();
	const atendidoForm = await superValidate(atendido, zod4(atendidoUpdateFormSchema));

	let assistidoForm = null;
	if (atendido.assistido) {
		assistidoForm = await superValidate(atendido.assistido, zod4(assistidoUpdateFormSchema));
	}

	return {
		form: atendidoForm,
		atendidoForm,
		assistidoForm,
		atendido,
		isAssistido: !!atendido.assistido
	};
};
