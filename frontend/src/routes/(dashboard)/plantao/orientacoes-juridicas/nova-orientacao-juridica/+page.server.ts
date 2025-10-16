import { superValidate } from 'sveltekit-superforms';
import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from '@sveltejs/kit';
import { zod4 } from 'sveltekit-superforms/adapters';
import { orientacaoJuridicaCreateFormSchema } from '$lib/forms/schemas/orientacao-juridica-schema';

export const load = async () => {
	const form = await superValidate(zod4(orientacaoJuridicaCreateFormSchema));
	return { form };
};

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const form = await superValidate(request, zod4(orientacaoJuridicaCreateFormSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const response = await fetch(`/api/orientacao_juridica`, {
			method: 'POST',
			body: JSON.stringify(form.data),
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			return fail(response.status, { form });
		}

		return redirect(302, `/plantao/orientacoes-juridicas`);
	}
};
