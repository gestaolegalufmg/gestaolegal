import { fail, redirect } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import type { Actions, PageServerLoad } from './$types';
import { passwordChangeSchema } from '$lib/forms/schemas/password-schema';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const userId = params.id;

	const [userResponse, meResponse] = await Promise.all([
		fetch(`/api/user/${userId}`),
		fetch(`/api/user/me`)
	]);

	if (!userResponse.ok) {
		throw new Error('Usuário não encontrado');
	}

	const user = await userResponse.json();
	const me = await meResponse.json();

	const form = await superValidate(zod4(passwordChangeSchema));

	return {
		user,
		me,
		form
	};
};

export const actions: Actions = {
	default: async ({ request, params, fetch }) => {
		const userId = params.id;
		const form = await superValidate(request, zod4(passwordChangeSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const meResponse = await fetch(`/api/user/me`);
		const me = await meResponse.json();

		const isAdmin = me.urole === 'admin';
		const isOwnProfile = me.id === parseInt(userId);

		const response = await fetch(`/api/user/${userId}/password`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				currentPassword: form.data.currentPassword,
				newPassword: form.data.newPassword,
				fromAdmin: isAdmin && !isOwnProfile
			})
		});

		if (!response.ok) {
			const errorData = await response.json();
			return fail(response.status, {
				form,
				message: errorData.message || 'Erro ao alterar senha'
			});
		}

		return redirect(302, `/usuarios/${userId}`);
	}
};
