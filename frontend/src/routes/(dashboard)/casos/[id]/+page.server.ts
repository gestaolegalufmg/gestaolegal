import { error, fail, redirect } from '@sveltejs/kit';
import type { Caso, Paginated } from '$lib/types';
import { message, superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { processoCreateFormSchema } from '$lib/forms/schemas/processo-schema.js';
import { eventoCreateFormSchema } from '$lib/forms/schemas/evento-schema.js';
import type { Evento } from '$lib/types/evento';

export const actions = {
	createProcesso: async ({ request, params, fetch }) => {
		const form = await superValidate(request, zod4(processoCreateFormSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const response = await fetch(`/api/caso/${params.id}/processos`, {
			method: 'POST',
			body: JSON.stringify(form.data)
		});

		if (!response.ok) {
			return fail(400, { form });
		}

		return redirect(302, `/casos/${params.id}`);
	},

	createEvento: async ({ request, params, fetch }) => {
		const formData = await request.formData();
		const form = await superValidate(formData, zod4(eventoCreateFormSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const requestFormData = new FormData();
		requestFormData.append('tipo', form.data.tipo);
		requestFormData.append('data_evento', form.data.data_evento);
		requestFormData.append('status', form.data.status.toString());

		if (form.data.descricao) {
			requestFormData.append('descricao', form.data.descricao);
		}

		if (
			form.data.id_usuario_responsavel !== null &&
			form.data.id_usuario_responsavel !== undefined
		) {
			requestFormData.append('id_usuario_responsavel', form.data.id_usuario_responsavel.toString());
		}

		if (form.data.arquivo && form.data.arquivo.size > 0) {
			requestFormData.append('arquivo', form.data.arquivo);
		}

		const response = await fetch(`/api/caso/${params.id}/eventos`, {
			method: 'POST',
			body: requestFormData
		});

		if (!response.ok) {
			return fail(400, { form });
		}

		return message(form, { message: 'Evento criado com sucesso' });
	}
};
