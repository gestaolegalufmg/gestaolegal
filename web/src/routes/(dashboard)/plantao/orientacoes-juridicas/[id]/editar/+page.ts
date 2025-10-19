import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { orientacaoJuridicaUpdateFormSchema } from '$lib/forms/schemas/orientacao-juridica-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';
import { ApiException } from '$lib/types';
import type { OrientacaoJuridica } from '$lib/types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const orientacao = await api.get<OrientacaoJuridica>(
			`orientacao_juridica/${params.id}`,
			{},
			fetch
		);

		const formData = {
			area_direito: orientacao.area_direito,
			sub_area: orientacao.sub_area,
			descricao: orientacao.descricao,
			atendidos_ids: orientacao.atendidos?.map((a: { id: number }) => a.id) ?? []
		};

		const form = await superValidate(formData, zod4(orientacaoJuridicaUpdateFormSchema));

		return { form, orientacao };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 404, err.message);
		}
		throw err;
	}
};
