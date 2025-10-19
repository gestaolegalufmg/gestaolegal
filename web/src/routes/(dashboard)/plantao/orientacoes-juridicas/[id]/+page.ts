import { error } from '@sveltejs/kit';
import type { OrientacaoJuridica } from '$lib/types';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { ApiException } from '$lib/types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const orientacao = await api.get<OrientacaoJuridica>(
			`orientacao_juridica/${params.id}`,
			{},
			fetch
		);

		return { orientacao };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 404, err.message);
		}
		throw err;
	}
};
