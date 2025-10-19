import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { processoCreateFormSchema } from '$lib/forms/schemas/processo-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';
import { flattenObject } from '$lib/utils/object';
import { ApiException } from '$lib/types';
import type { Processo } from '$lib/types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const processo = await api.get<Processo>(
			`caso/${params.id}/processos/${params.processoId}`,
			{},
			fetch
		);

		const processoFlattened = flattenObject(processo);
		const parsed = processoCreateFormSchema.parse(processoFlattened);
		const form = await superValidate(parsed, zod4(processoCreateFormSchema));

		return { form, processo };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
