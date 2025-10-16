import { error } from '@sveltejs/kit';
import type { Paginated, User } from '$lib/types';
import { zod4 } from 'sveltekit-superforms/adapters';
import { superValidate } from 'sveltekit-superforms/client';
import { z } from 'zod/v4';

const userSearchSchema = z.object({
	search: z.string().optional().default(''),
	show_inactive: z.boolean().optional().default(false),
	funcao: z.string().optional().default('all')
});

export const load = async ({ fetch, depends, url, parent }) => {
	depends('app:usuarios');

	const urlParams = url.searchParams;
	const { me } = await parent();
	const emptyUsers: Paginated<User> = {
		items: [],
		total: 0,
		page: 1,
		per_page: 10
	};

	const formData = await superValidate(
		{
			search: urlParams.get('search') || '',
			show_inactive: urlParams.get('show_inactive') === 'true',
			funcao: urlParams.get('funcao') || 'all'
		},
		zod4(userSearchSchema)
	);

	if (me.urole !== 'admin') {
		return {
			users: emptyUsers,
			formData,
			canManageUsers: false
		};
	}

	const response = await fetch(`/api/user?${urlParams.toString()}`);

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
