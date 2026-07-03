import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { assistenciaJudiciariaUpdateFormSchema } from '$lib/forms/schemas/assistencia-judiciaria-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';
import { ApiException } from '$lib/types';
import type { AssistenciaJudiciaria } from '$lib/types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const assistencia = await api.get<AssistenciaJudiciaria>(
			`assistencia_judiciaria/${params.id}`,
			{},
			fetch
		);

		const formData = {
			nome: assistencia.nome,
			regiao: assistencia.regiao,
			areas_atendidas: assistencia.areas_atendidas ?? [],
			telefone: assistencia.telefone,
			email: assistencia.email,
			logradouro: assistencia.endereco?.logradouro ?? '',
			numero: assistencia.endereco?.numero ?? '',
			complemento: assistencia.endereco?.complemento ?? '',
			bairro: assistencia.endereco?.bairro ?? '',
			cep: assistencia.endereco?.cep ?? '',
			cidade: assistencia.endereco?.cidade ?? '',
			estado: assistencia.endereco?.estado ?? ''
		};

		const form = await superValidate(formData, zod4(assistenciaJudiciariaUpdateFormSchema));

		return { form, assistencia };
	} catch (err) {
		if (err instanceof ApiException) {
			error(err.statusCode || 404, err.message);
		}
		throw err;
	}
};
