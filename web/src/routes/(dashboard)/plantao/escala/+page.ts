import { api } from '$lib/api-client';
import { ApiException, type PaginaPlantao } from '$lib/types';
import { error } from '@sveltejs/kit';

export const load = async ({ fetch }) => {
	try {
		const pagina = await api.get<PaginaPlantao>('plantao', {}, fetch);
		return { pagina };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
