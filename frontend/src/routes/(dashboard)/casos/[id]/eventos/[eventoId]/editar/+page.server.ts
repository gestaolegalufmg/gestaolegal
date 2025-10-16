import { error, fail, redirect } from '@sveltejs/kit';
import type { Evento } from '$lib/types/evento';
import type { Caso } from '$lib/types';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { eventoUpdateFormSchema } from '$lib/forms/schemas/evento-schema';
import type { Actions } from '@sveltejs/kit';

export const load = async ({ params, fetch }) => {
	const eventoResponse = await fetch(`/api/caso/${params.id}/eventos/${params.eventoId}`);

	if (!eventoResponse.ok) {
		error(404, 'Caso não encontrado');
	}

	if (!eventoResponse.ok) {
		error(404, 'Evento não encontrado');
	}

	const evento: Evento = await eventoResponse.json();

	const form = await superValidate(
		{
			tipo: evento.tipo,
			descricao: evento.descricao || '',
			data_evento: evento.data_evento,
			id_usuario_responsavel: evento.id_usuario_responsavel || null,
			status: evento.status,
			arquivo: null
		},
		zod4(eventoUpdateFormSchema)
	);

	return {
		evento,
		form
	};
};

export const actions: Actions = {
	default: async ({ request, params, fetch }) => {
		const formData = await request.formData();
		const form = await superValidate(formData, zod4(eventoUpdateFormSchema));

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

		const response = await fetch(`/api/caso/${params.id}/eventos/${params.eventoId}`, {
			method: 'PUT',
			body: requestFormData
		});

		if (!response.ok) {
			return fail(400, { form });
		}

		return redirect(302, `/casos/${params.id}/eventos/${params.eventoId}`);
	}
};
