import type { ListCaso, Paginated } from '$lib/types';
import { api } from '$lib/api-client';

export const load = async ({ url, fetch }) => {
	const urlParams = url.searchParams;
	const response = await api.get(`caso?${urlParams.toString()}`, {}, fetch);

	const data: Paginated<ListCaso> = await response.json();

	return { data };
};
