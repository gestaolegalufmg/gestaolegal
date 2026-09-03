import { api } from '$lib/api-client';
import { ApiException, type Arquivo } from '$lib/types';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const arquivo = await api.get<Arquivo>(`arquivo/${params.id}`, {}, fetch);
		return { arquivo };
	} catch (err) {
		if (err instanceof ApiException) error(err.statusCode || 404, err.message);
		throw err;
	}
};
