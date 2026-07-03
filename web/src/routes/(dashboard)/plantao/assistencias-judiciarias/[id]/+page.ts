import { error } from '@sveltejs/kit';
import type { AssistenciaJudiciaria } from '$lib/types';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { ApiException } from '$lib/types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const assistencia = await api.get<AssistenciaJudiciaria>(
			`assistencia_judiciaria/${params.id}`,
			{},
			fetch
		);

		return { assistencia };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 404, err.message);
		}
		throw err;
	}
};
