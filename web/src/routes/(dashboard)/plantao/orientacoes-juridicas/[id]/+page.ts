import { error } from '@sveltejs/kit';
import type { ListAssistenciaJudiciaria, OrientacaoJuridica } from '$lib/types';
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

		let assistencias: ListAssistenciaJudiciaria[] = [];
		try {
			assistencias = await api.get<ListAssistenciaJudiciaria[]>(
				`assistencia_judiciaria?orientacao_id=${params.id}`,
				{},
				fetch
			);
		} catch {
			assistencias = [];
		}

		return { orientacao, assistencias };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 404, err.message);
		}
		throw err;
	}
};
