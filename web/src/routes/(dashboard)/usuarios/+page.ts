import { error } from '@sveltejs/kit';
import type { Paginated, User } from '$lib/types';
import { userSearchSchema } from '$lib/forms/schemas/user-schema';
import { zod4 } from 'sveltekit-superforms/adapters';
import { superValidate } from 'sveltekit-superforms/client';
import { api } from '$lib/api-client';

export const load = async ({ depends, url, fetch }) => {
	depends('app:usuarios');

	const urlParams = url.searchParams;

	const formData = await superValidate(
		{
			search: urlParams.get('search') || '',
			show_inactive: urlParams.get('show_inactive') === 'true',
			funcao: urlParams.get('funcao') || 'all'
		},
		zod4(userSearchSchema)
	);

	const response = await api.get(`user?${urlParams.toString()}`, {}, fetch);

	if (!response.ok) {
		error(response.status, 'Falha ao carregar usuários');
	}

	const data: Paginated<User> = await response.json();

	return {
		users: data,
		formData,
		canManageUsers: true
	};
};
