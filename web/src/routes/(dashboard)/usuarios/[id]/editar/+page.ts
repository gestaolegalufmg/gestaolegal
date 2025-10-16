import { userUpdateFormSchema } from '$lib/forms/schemas/user-schema';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import type { User } from '$lib/types/user';
import { flattenObject } from '$lib/utils/object';

export const load: PageLoad = async ({ params, fetch, parent }) => {
	if (params.id === 'eu') {
		const { me } = await parent();
		return {
			form: await superValidate(me, zod4(userUpdateFormSchema)),
			user: me
		};
	}

	const userResponse = await api.get(`user/${params.id}`, {}, fetch);

	if (!userResponse.ok) {
		throw new Error('Usuário não encontrado');
	}

	const user: User = await userResponse.json();
	const form = await superValidate(flattenObject(user), zod4(userUpdateFormSchema));

	return { form, user };
};
