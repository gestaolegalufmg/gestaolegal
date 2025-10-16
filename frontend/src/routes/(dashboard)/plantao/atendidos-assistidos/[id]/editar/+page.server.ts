import { superValidate } from 'sveltekit-superforms';
import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions } from '@sveltejs/kit';
import { zod4 } from 'sveltekit-superforms/adapters';
import { atendidoUpdateFormSchema } from '$lib/forms/schemas/atendido-schema';
import { assistidoUpdateFormSchema } from '$lib/forms/schemas/assistido-schema';

export const load = async ({ params, fetch }) => {
	const response = await fetch(`/api/atendido/${params.id}`);

	if (!response.ok) {
		error(response.status);
	}

	const atendido = await response.json();
	const atendidoForm = await superValidate(atendido, zod4(atendidoUpdateFormSchema));

	let assistidoForm = null;
	if (atendido.assistido) {
		assistidoForm = await superValidate(atendido.assistido, zod4(assistidoUpdateFormSchema));
	}

	return {
		form: atendidoForm,
		atendidoForm,
		assistidoForm,
		atendido,
		isAssistido: !!atendido.assistido
	};
};

export const actions: Actions = {
	default: async ({ request, params, fetch }) => {
		const formData = await request.formData();
		const isAssistido = formData.get('isAssistido') === 'true';

		const atendidoForm = await superValidate(formData, zod4(atendidoUpdateFormSchema));

		if (!atendidoForm.valid) {
			return fail(400, { atendidoForm });
		}

		if (isAssistido) {
			const assistidoForm = await superValidate(formData, zod4(assistidoUpdateFormSchema));

			if (!assistidoForm.valid) {
				return fail(400, { atendidoForm, assistidoForm });
			}

			const combinedData = {
				...atendidoForm.data,
				...assistidoForm.data
			};

			const response = await fetch(`/api/atendido/${params.id}/assistido`, {
				method: 'PUT',
				body: JSON.stringify(combinedData),
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) {
				return fail(response.status, { atendidoForm, assistidoForm });
			}
		} else {
			const response = await fetch(`/api/atendido/${params.id}`, {
				method: 'PUT',
				body: JSON.stringify(atendidoForm.data),
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) {
				return fail(response.status, { atendidoForm });
			}
		}

		return redirect(302, `/plantao/atendidos-assistidos`);
	}
};
