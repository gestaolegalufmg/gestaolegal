import { api } from '$lib/api-client';
import { ApiException, type ConfiguracaoPlantao } from '$lib/types';
import { error } from '@sveltejs/kit';

const PAPEIS_PERMITIDOS = ['admin', 'colab_proj'];

export const load = async ({ fetch, parent }) => {
	const { me } = await parent();
	if (!PAPEIS_PERMITIDOS.includes(me.urole)) {
		error(403, 'Você não tem permissão para acessar esta página. Contate o administrador.');
	}

	try {
		const configuracao = await api.get<ConfiguracaoPlantao>('plantao/configuracao', {}, fetch);
		return { configuracao };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
