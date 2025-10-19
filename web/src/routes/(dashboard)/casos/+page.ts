import type { ListCaso, Paginated } from '$lib/types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';
import { ApiException } from '$lib/types';

export const load = async ({ url, fetch }) => {
	const urlParams = url.searchParams;

	try {
		const data = await api.get<Paginated<ListCaso>>(`caso?${urlParams.toString()}`, {}, fetch);
		return { data };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
