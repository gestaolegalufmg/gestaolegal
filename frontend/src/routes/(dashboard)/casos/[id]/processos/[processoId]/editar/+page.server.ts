import { superValidate } from 'sveltekit-superforms';
import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions } from '@sveltejs/kit';
import { zod4 } from 'sveltekit-superforms/adapters';
import { processoCreateFormSchema } from '$lib/forms/schemas/processo-schema';
import type { Processo } from '$lib/types';
import { flattenObject } from '$lib/utils/object.js';

export const load = async ({ params, fetch }) => {
	const processo: Processo = await fetch(
		`/api/caso/${params.id}/processos/${params.processoId}`
	).then((res) => res.json());

	const processoFlattened = flattenObject(processo);

	const parsed = processoCreateFormSchema.parse(processoFlattened);

	const form = await superValidate(parsed, zod4(processoCreateFormSchema));
	return { form, processo };
};

export const actions: Actions = {
	default: async (event) => {
		const { fetch } = event;

		const form = await superValidate(event, zod4(processoCreateFormSchema));
		if (!form.valid) {
			return fail(400, { form });
		}

		const response = await fetch(
			`/api/caso/${event.params.id}/processos/${event.params.processoId}`,
			{
				method: 'PUT',
				body: JSON.stringify(form.data),
				headers: {
					'Content-Type': 'application/json'
				}
			}
		);

		if (response.status !== 200) {
			error(500, 'Erro ao atualizar processo');
		}

		return redirect(302, `/casos/${event.params.id}/processos/${event.params.processoId}`);
	}
};
