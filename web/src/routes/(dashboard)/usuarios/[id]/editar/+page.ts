import { userUpdateFormSchema } from '$lib/forms/schemas/user-schema';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import type { User } from '$lib/types/user';
import { flattenObject } from '$lib/utils/object';
import { error } from '@sveltejs/kit';
import { ApiException } from '$lib/types';

export const load: PageLoad = async ({ params, fetch, parent }) => {
	if (params.id === 'eu') {
		const { me } = await parent();
		return {
			form: await superValidate(me, zod4(userUpdateFormSchema)),
			user: me
		};
	}

	try {
		const user = await api.get<User>(`user/${params.id}`, {}, fetch);
		const form = await superValidate(flattenObject(user), zod4(userUpdateFormSchema));

		return { form, user };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 404, err.message);
		}
		throw err;
	}
};
