import { api } from '$lib/api-client';
import { ApiException, type Pendencias } from '$lib/types';
import { error } from '@sveltejs/kit';

const PAPEIS_PERMITIDOS = ['admin', 'colab_proj', 'prof'];

export const load = async ({ fetch, parent }) => {
	const { me } = await parent();
	if (!PAPEIS_PERMITIDOS.includes(me.urole)) {
		error(403, 'Você não tem permissão para acessar essa página');
	}

	try {
		const pendencias = await api.get<Pendencias>('presenca/confirmacao', {}, fetch);
		return { pendencias };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
