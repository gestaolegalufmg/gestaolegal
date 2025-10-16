import { superValidate } from 'sveltekit-superforms';
import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions } from '@sveltejs/kit';
import { zod4 } from 'sveltekit-superforms/adapters';
import { casoCreateFormSchema } from '$lib/forms/schemas/caso-schema';
import type { User } from '$lib/types';

export const load = async ({ params, fetch }) => {
	const casoResponse = await fetch(`/api/caso/${params.id}`);

	if (!casoResponse.ok) {
		error(casoResponse.status);
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
		ids_clientes: caso.clientes?.map((c: any) => c.id) || []
	};

	const form = await superValidate(casoData, zod4(casoCreateFormSchema));

	const usersResponse = await fetch(`/api/user?per_page=1000`);
	const usersData = await usersResponse.json();
	const usuarios: User[] = usersData.items || [];

	const casoAssistidos = caso.clientes || [];

	return { form, usuarios, assistidos: casoAssistidos, caso };
};

export const actions: Actions = {
	default: async ({ request, params, fetch }) => {
		const form = await superValidate(request, zod4(casoCreateFormSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const response = await fetch(`/api/caso/${params.id}`, {
			method: 'PUT',
			body: JSON.stringify(form.data),
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			const errorText = await response.text();
			return fail(response.status, { form, error: errorText });
		}

		return redirect(302, `/casos/${params.id}`);
	}
};
