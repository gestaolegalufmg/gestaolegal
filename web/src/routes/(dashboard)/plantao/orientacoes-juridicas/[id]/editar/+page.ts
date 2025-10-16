import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { orientacaoJuridicaUpdateFormSchema } from '$lib/forms/schemas/orientacao-juridica-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';

export const load: PageLoad = async ({ params, fetch }) => {
	const response = await api.get(`orientacao_juridica/${params.id}`, {}, fetch);

	if (!response.ok) {
		error(response.status, 'Orientacao juridica nao encontrada');
	}

	const orientacao = await response.json();

	const formData = {
		area_direito: orientacao.area_direito,
		sub_area: orientacao.sub_area,
		descricao: orientacao.descricao,
		atendidos_ids: orientacao.atendidos?.map((a: { id: number }) => a.id) ?? []
	};

	const form = await superValidate(formData, zod4(orientacaoJuridicaUpdateFormSchema));

	return { form, orientacao };
};
