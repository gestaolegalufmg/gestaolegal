import type { Actions } from '@sveltejs/kit';
import { fail, superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { z } from 'zod';

const passwordSchema = z
	.object({
		currentPassword: z.string().min(1, 'Senha atual é obrigatória'),
		newPassword: z.string().min(8, 'Nova senha deve ter pelo menos 8 caracteres'),
		confirmPassword: z.string().min(1, 'Confirmação de senha é obrigatória')
	})
	.refine((data) => data.newPassword === data.confirmPassword, {
		message: 'As senhas não coincidem',
		path: ['confirmPassword']
	});

export const load = async ({ fetch }) => {
	const meResponse = await fetch(`/api/user/me`);
	const me = await meResponse.json();

	const form = await superValidate(zod4(passwordSchema));

	return {
		me,
		form
	};
};

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const formData = await request.formData();

		const data = {
			currentPassword: formData.get('currentPassword') as string,
			newPassword: formData.get('newPassword') as string,
			confirmPassword: formData.get('confirmPassword') as string
		};

		const form = await superValidate(data, zod4(passwordSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		try {
			const meResponse = await fetch(`/api/user/me`);
			const me = await meResponse.json();

			const response = await fetch(`/api/user/${me.id}/password`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					currentPassword: data.currentPassword,
					newPassword: data.newPassword,
					fromAdmin: false
				})
			});

			if (!response.ok) {
				const errorData = await response.json();
				return fail(response.status, {
					form,
					message: errorData.message || 'Erro ao alterar senha'
				});
			}

			return { form, success: true };
		} catch (error) {
			return fail(500, {
				form,
				message: 'Erro interno do servidor'
			});
		}
	}
};
