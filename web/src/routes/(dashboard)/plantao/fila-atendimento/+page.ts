import type { FilaItem } from '$lib/types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';
import { ApiException } from '$lib/types';

export const load = async ({ fetch }) => {
	try {
		const fila = await api.get<FilaItem[]>('fila_atendimento', {}, fetch);
		return { fila };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
