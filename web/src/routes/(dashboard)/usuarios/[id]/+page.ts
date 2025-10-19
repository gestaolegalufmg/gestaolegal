import { error } from '@sveltejs/kit';
import type { User } from '$lib/types';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { ApiException } from '$lib/types';

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

	try {
		const user = await api.get<User>(`user/${params.id}`, {}, fetch);

		return {
			user,
			canView: true
		};
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
