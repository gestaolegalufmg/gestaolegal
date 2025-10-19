import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { ApiException } from '$lib/types';
import type { Atendido } from '$lib/types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const atendido = await api.get<Atendido>(`atendido/${params.id}`, {}, fetch);

		return { atendido };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 404, err.message);
		}
		throw err;
	}
};
