import { error } from '@sveltejs/kit';
import type { User } from '$lib/types';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch, parent }) => {
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
		const response = await fetch(`/api/user/me`);

		if (!response.ok) {
			error(response.status, 'Falha ao carregar usuário');
		}

		return {
			user: (await response.json()) as User,
			canView: true
		};
	}

	const response = await fetch(`/api/user/${params.id}`);

	if (!response.ok) {
		error(response.status, 'Falha ao carregar usuário');
	}

	return {
		user: (await response.json()) as User,
		canView: true
	};
};
