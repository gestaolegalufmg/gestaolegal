import { api } from '$lib/api-client';
import { ApiException, type EstadoPresenca } from '$lib/types';
import { error } from '@sveltejs/kit';

export const load = async ({ fetch }) => {
	try {
		const estado = await api.get<EstadoPresenca>('presenca/registro', {}, fetch);
		return { estado };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
