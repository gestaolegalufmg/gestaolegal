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
		// Esta tela é a única que pede as inativas junto (`incluir_inativas=1`,
		// só honrado para admin): é por aqui que uma unidade desativada volta a
		// aparecer para ser reativada. A barra final evita o redirect do Flask.
		const unidades = await api.get<Unidade[]>('unidades/?incluir_inativas=1', {}, fetch);
		return { unidades };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
