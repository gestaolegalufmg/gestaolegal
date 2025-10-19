import { superValidate } from 'sveltekit-superforms';
import { error } from '@sveltejs/kit';
import { zod4 } from 'sveltekit-superforms/adapters';
import { assistidoCreateFormSchema } from '$lib/forms/schemas/assistido-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { ApiException } from '$lib/types';
import type { Atendido } from '$lib/types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const atendido = await api.get<Atendido>(`atendido/${params.id}`, {}, fetch);

		if (atendido.assistido) {
			error(400, 'Este atendido já é um assistido');
		}

		const form = await superValidate(zod4(assistidoCreateFormSchema));

		return { form, atendido };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 404, err.message);
		}
		throw err;
	}
};
