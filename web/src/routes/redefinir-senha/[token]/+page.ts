import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { resetPasswordSchema } from '$lib/forms/schemas/reset-password-schema';
import { api } from '$lib/api-client';

export const load = async ({ params, fetch }) => {
	const form = await superValidate(zod4(resetPasswordSchema));
	// Um link inválido não é erro de servidor: a página explica o que houve e
	// oferece o caminho para pedir outro.
	try {
		await api.get(`auth/reset-password/${params.token}/validate`, {}, fetch);
		return { form, tokenValido: true };
	} catch {
		return { form, tokenValido: false };
	}
};
