import { superValidate } from 'sveltekit-superforms';
import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions } from '@sveltejs/kit';
import { zod4 } from 'sveltekit-superforms/adapters';
import { orientacaoJuridicaUpdateFormSchema } from '$lib/forms/schemas/orientacao-juridica-schema';
import type { OrientacaoJuridica } from '$lib/types';

export const load = async ({ params, fetch }) => {
	const response = await fetch(`/api/orientacao_juridica/${params.id}`);

	if (!response.ok) {
		error(response.status, 'Orientação Jurídica não encontrada');
	}

	const orientacao = (await response.json()) as OrientacaoJuridica;

	const formData = {
		area_direito: orientacao.area_direito as
			| 'administrativo'
			| 'ambiental'
			| 'civel'
			| 'empresarial'
			| 'penal'
			| 'trabalhista',
		sub_area: orientacao.sub_area,
		descricao: orientacao.descricao,
		atendidos_ids: orientacao.atendidos?.map((a) => a.id) || []
	};

	const form = await superValidate(formData, zod4(orientacaoJuridicaUpdateFormSchema));
	return { form, orientacao };
};

export const actions: Actions = {
	default: async (event) => {
		const { fetch, request } = event;

		const form = await superValidate(request, zod4(orientacaoJuridicaUpdateFormSchema));
		if (!form.valid) {
			return fail(400, { form });
		}

		const response = await fetch(`/api/orientacao_juridica/${event.params.id}`, {
			method: 'PUT',
			body: JSON.stringify(form.data),
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (response.status !== 200) {
			error(500, 'Erro ao atualizar orientação jurídica');
		}

		return redirect(302, `/plantao/orientacoes-juridicas/${event.params.id}`);
	}
};
