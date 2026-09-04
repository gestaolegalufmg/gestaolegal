import { error } from '@sveltejs/kit';
import { api } from '$lib/api-client';
import { ApiException, type Unidade } from '$lib/types';

export const load = async ({ parent, fetch, depends }) => {
	const { me } = await parent();
	if (me.urole !== 'admin') {
		error(403, 'Você não tem permissão para gerenciar unidades. Contate o administrador.');
	}

	depends('app:unidades');

	try {
		// `GET /api/unidades/` devolve só as ativas; a barra final evita o
		// redirect do Flask.
		const unidades = await api.get<Unidade[]>('unidades/', {}, fetch);
		return { unidades };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
