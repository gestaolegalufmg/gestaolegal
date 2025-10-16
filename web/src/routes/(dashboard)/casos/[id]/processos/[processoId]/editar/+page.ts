import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { processoCreateFormSchema } from '$lib/forms/schemas/processo-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';
import { flattenObject } from '$lib/utils/object';

export const load: PageLoad = async ({ params, fetch }) => {
	const processoResponse = await api.get(
		`caso/${params.id}/processos/${params.processoId}`,
		{},
		fetch
	);

	if (!processoResponse.ok) {
		error(processoResponse.status, 'Processo nao encontrado');
	}

	const processo = await processoResponse.json();
	const processoFlattened = flattenObject(processo);
	const parsed = processoCreateFormSchema.parse(processoFlattened);

	const form = await superValidate(parsed, zod4(processoCreateFormSchema));

	return { form, processo };
};
