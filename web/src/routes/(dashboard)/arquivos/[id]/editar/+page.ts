import { api } from '$lib/api-client';
import { ApiException, ARQUIVO_PAPEIS_EDITAM, type Arquivo } from '$lib/types';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch, parent }) => {
	const { me } = await parent();
	if (!ARQUIVO_PAPEIS_EDITAM.includes(me.urole)) {
		error(403, 'Você não tem permissão para editar arquivos. Contate o administrador.');
	}
	try {
		const arquivo = await api.get<Arquivo>(`arquivo/${params.id}`, {}, fetch);
		return { arquivo };
	} catch (err) {
		if (err instanceof ApiException) error(err.statusCode || 404, err.message);
		throw err;
	}
};
