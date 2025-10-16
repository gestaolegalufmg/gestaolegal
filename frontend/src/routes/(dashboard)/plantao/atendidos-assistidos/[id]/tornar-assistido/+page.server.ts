import { superValidate } from 'sveltekit-superforms';
import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions } from '@sveltejs/kit';
import { zod4 } from 'sveltekit-superforms/adapters';
import { assistidoCreateFormSchema } from '$lib/forms/schemas/assistido-schema';

export const load = async ({ params, fetch }) => {
	const response = await fetch(`/api/atendido/${params.id}`);

	if (!response.ok) {
		error(response.status);
	}

	const atendido = await response.json();

	if (atendido.assistido) {
		error(400);
	}

	const form = await superValidate(zod4(assistidoCreateFormSchema));

	return { form, atendido };
};

export const actions: Actions = {
	default: async ({ request, params, fetch }) => {
		const form = await superValidate(request, zod4(assistidoCreateFormSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const response = await fetch(`/api/atendido/${params.id}/tornar-assistido`, {
			method: 'POST',
			body: JSON.stringify(form.data),
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			return fail(response.status, { form });
		}

		return redirect(302, `/plantao/atendidos-assistidos`);
	}
};
