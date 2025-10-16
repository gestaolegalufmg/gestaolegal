import { superValidate } from 'sveltekit-superforms';
import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions } from '@sveltejs/kit';
import { zod4 } from 'sveltekit-superforms/adapters';
import { casoCreateFormSchema } from '$lib/forms/schemas/caso-schema';
import type { User } from '$lib/types';

export const load = async ({ fetch }) => {
	const form = await superValidate(zod4(casoCreateFormSchema));

	const usersResponse = await fetch(`/api/user?per_page=1000`);
	const usersData = await usersResponse.json();
	const usuarios: User[] = usersData.items || [];

	return { form, usuarios, assistidos: [] };
};

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const form = await superValidate(request, zod4(casoCreateFormSchema));

		if (!form.valid) {
			return fail(500, { form });
		}

		const newCaso = await fetch(`/api/caso`, {
			method: 'POST',
			body: JSON.stringify(form.data),
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (!newCaso.ok) {
			const errorText = await newCaso.text();
			return fail(newCaso.status, { form, error: errorText });
		}

		const newCasoData: any = await newCaso.json();
		return redirect(302, `/casos/${newCasoData.id}`);
	}
};
