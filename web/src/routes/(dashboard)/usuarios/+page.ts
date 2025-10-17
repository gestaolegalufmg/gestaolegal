import { error } from '@sveltejs/kit';
import type { Paginated, User } from '$lib/types';
import { api } from '$lib/api-client';

export const load = async ({ url, fetch }) => {
	const urlParams = url.searchParams;

	const response = await api.get(`user?${urlParams.toString()}`, {}, fetch);

	if (!response.ok) {
		error(response.status, 'Falha ao carregar usuários');
	}

	const data: Paginated<User> = await response.json();

	return {
		users: data,
		canManageUsers: true
	};
};
