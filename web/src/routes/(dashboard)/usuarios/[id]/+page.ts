import { error } from '@sveltejs/kit';
import type { User } from '$lib/types';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';

export const load: PageLoad = async ({ params, parent, fetch }) => {
	const { me } = await parent();
	const isAdmin = me.urole === 'admin';
	const isCurrentUser = params.id === 'eu' || (me.id != null && params.id === String(me.id));

	if (!isAdmin && !isCurrentUser) {
		return {
			user: me,
			canView: false
		};
	}

	if (isCurrentUser) {
		return {
			user: me,
			canView: true
		};
	}

	const response = await api.get(`user/${params.id}`, {}, fetch);

	if (!response.ok) {
		error(response.status, 'Falha ao carregar usuário');
	}

	return {
		user: (await response.json()) as User,
		canView: true
	};
};
