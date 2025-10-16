import { superValidate } from 'sveltekit-superforms';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from '@sveltejs/kit';
import { zod4 } from 'sveltekit-superforms/adapters';
import { atendidoCreateFormSchema } from '$lib/forms/schemas/atendido-schema';

export const load = async () => {
	const form = await superValidate(zod4(atendidoCreateFormSchema));
	return { form };
};

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const form = await superValidate(request, zod4(atendidoCreateFormSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const response = await fetch(`/api/atendido`, {
			method: 'POST',
			body: JSON.stringify(form.data),
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			return fail(response.status, { form });
		}

		const newAtendido: any = await response.json();
		return redirect(302, `/plantao/atendidos-assistidos`);
	}
};
