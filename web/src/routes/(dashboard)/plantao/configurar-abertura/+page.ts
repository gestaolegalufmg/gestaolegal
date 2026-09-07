import { api } from '$lib/api-client';
import { ApiException, type ConfiguracaoPlantao } from '$lib/types';
import { error } from '@sveltejs/kit';

const PAPEIS_PERMITIDOS = ['admin', 'colab_proj'];

export const load = async ({ fetch, parent, url }) => {
	const { me } = await parent();
	if (!PAPEIS_PERMITIDOS.includes(me.urole)) {
		error(403, 'Você não tem permissão para acessar esta página. Contate o administrador.');
	}

	if (url.searchParams.get('nova') === '1')
		return {
			configuracao: {
				id: null,
				nome: '',
				legado: false,
				cancelado: false,
				dias: [],
				data_abertura: null,
				data_fechamento: null
			} as ConfiguracaoPlantao
		};
	const escalaId = url.searchParams.get('escala_id');
	if (!escalaId) error(400, 'Selecione uma escala na listagem.');
	try {
		const configuracao = await api.get<ConfiguracaoPlantao>(
			`plantao/configuracao?escala_id=${encodeURIComponent(escalaId)}`,
			{},
			fetch
		);
		if (configuracao.legado || configuracao.cancelado)
			error(403, 'Esta escala é somente para consulta.');
		return { configuracao };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
