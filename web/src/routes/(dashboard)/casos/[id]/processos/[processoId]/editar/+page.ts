import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { processoCreateFormSchema } from '$lib/forms/schemas/processo-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';
import { toISODateInput } from '$lib/utils/date';
import { ApiException } from '$lib/types';
import type { Processo } from '$lib/types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const processo = await api.get<Processo>(
			`caso/${params.id}/processos/${params.processoId}`,
			{},
			fetch
		);

		// Não achatar os relacionamentos: obs/status do criador não são os do processo.
		const form = await superValidate(
			{
				...processo,
				data_distribuicao: toISODateInput(processo.data_distribuicao) ?? null,
				data_transito_em_julgado: toISODateInput(processo.data_transito_em_julgado) ?? null
			},
			zod4(processoCreateFormSchema),
			{ id: `processo-editar-${params.processoId}` }
		);

		return { form, processo };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 500, err.message);
		}
		throw err;
	}
};
