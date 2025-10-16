import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { casoCreateFormSchema } from '$lib/forms/schemas/caso-schema';
import type { PageLoad } from './$types';
import { api } from '$lib/api-client';
import { error } from '@sveltejs/kit';

export const load: PageLoad = async ({ params, fetch }) => {
	const casoResponse = await api.get(`caso/${params.id}`, {}, fetch);

	if (!casoResponse.ok) {
		error(casoResponse.status, 'Caso nao encontrado');
	}

	const caso = await casoResponse.json();

	const casoData = {
		id_usuario_responsavel: caso.id_usuario_responsavel,
		area_direito: caso.area_direito,
		sub_area: caso.sub_area,
		id_orientador: caso.id_orientador,
		id_estagiario: caso.id_estagiario,
		id_colaborador: caso.id_colaborador,
		situacao_deferimento: caso.situacao_deferimento,
		justif_indeferimento: caso.justif_indeferimento,
		descricao: caso.descricao,
		ids_clientes: caso.clientes?.map((cliente: { id: number }) => cliente.id) ?? []
	};

	const form = await superValidate(casoData, zod4(casoCreateFormSchema));

	const usersResponse = await api.get('user?per_page=1000', {}, fetch);

	if (!usersResponse.ok) {
		error(usersResponse.status, 'Nao foi possivel carregar usuarios');
	}

	const usersData = await usersResponse.json();
	const usuarios = usersData.items ?? [];
	const casoAssistidos = caso.clientes ?? [];

	return { form, usuarios, assistidos: casoAssistidos, caso };
};
