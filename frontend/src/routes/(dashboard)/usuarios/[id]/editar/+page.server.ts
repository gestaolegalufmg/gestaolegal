import { superValidate } from 'sveltekit-superforms';
import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions } from '@sveltejs/kit';
import { zod4 } from 'sveltekit-superforms/adapters';
import { userUpdateFormSchema } from '$lib/forms/schemas/user-schema';
import type { User } from '$lib/types/user.js';
import { flattenObject } from '$lib/utils/object.js';

export const load = async ({ params, fetch }) => {
	const route = params.id === 'eu' ? 'me' : params.id;
	const user: User = await fetch(`/api/user/${route}`).then((res) => res.json());

	const userFlattened = flattenObject(user);

	const parsed = userUpdateFormSchema.parse(userFlattened);

	const form = await superValidate(parsed, zod4(userUpdateFormSchema));
	return { form, user };
};

export const actions: Actions = {
	default: async (event) => {
		const { fetch } = event;

		const form = await superValidate(event, zod4(userUpdateFormSchema));
		if (!form.valid) {
			return fail(400, { form });
		}

		const identifier = event.params.id === 'eu' ? 'me' : event.params.id;
		const response = await fetch(`/api/user/${identifier}`, {
			method: 'PUT',
			body: JSON.stringify(form.data)
		});

		if (response.status !== 200) {
			error(500, 'Erro ao atualizar usuário');
		}

		return redirect(302, `/usuarios/${event.params.id}`);
	}
};
