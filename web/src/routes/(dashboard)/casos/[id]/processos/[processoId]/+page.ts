import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { ApiException } from '$lib/types';
import type { Processo } from '$lib/types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const processo = await api.get<Processo>(
			`caso/${params.id}/processos/${params.processoId}`,
			{},
			fetch
		);

		return { processo };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 404, err.message);
		}
		throw err;
	}
};
