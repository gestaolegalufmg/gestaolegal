import { superValidate } from 'sveltekit-superforms';
import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions } from '@sveltejs/kit';
import { zod4 } from 'sveltekit-superforms/adapters';
import { userCreateFormSchema } from '$lib/forms/schemas/user-schema';

export const load = async () => {
	const form = await superValidate(zod4(userCreateFormSchema));
	return { form };
};

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const form = await superValidate(request, zod4(userCreateFormSchema));

		if (!form.valid) {
			return fail(500, { form });
		}

		const newUser = await fetch(`/api/user`, {
			method: 'POST',
			body: JSON.stringify(form.data),
			headers: {
				'Content-Type': 'application/json'
			}
		});

		const newUserData: any = await newUser.json();
		return redirect(302, `/usuarios/${newUserData.id}`);
	}
};
