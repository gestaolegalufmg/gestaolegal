import type { ListAtendido, Paginated } from '$lib/types';
import { api } from '$lib/api-client';

export const load = async ({ depends, url, fetch }) => {
	depends('app:atendidos');

	const urlParams = url.searchParams;
	const response = await api.get(`atendido?${urlParams.toString()}`, {}, fetch);

	const data: Paginated<ListAtendido> = await response.json();

	return { data };
};
