import type { ListAtendido, Paginated } from '$lib/types';
import { api } from '$lib/api-client';

export const load = async ({ url, fetch }) => {
	const urlParams = url.searchParams;
	const response = await api.get(`atendido?${urlParams.toString()}`, {}, fetch);

	const data: Paginated<ListAtendido> = await response.json();

	return { atendidos: data };
};
