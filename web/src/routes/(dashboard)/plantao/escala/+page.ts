import { api } from '$lib/api-client';
import { ApiException, type PaginaPlantao } from '$lib/types';
import { error, redirect } from '@sveltejs/kit';

export const load = async ({ fetch, url }) => {
	const escalaId = url.searchParams.get('escala_id');
	if (!escalaId) redirect(307, '/plantao/escalas');
	try {
		const pagina = await api.get<PaginaPlantao>(
			`plantao?escala_id=${encodeURIComponent(escalaId)}`,
			{},
			fetch
		);
		return { pagina };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
