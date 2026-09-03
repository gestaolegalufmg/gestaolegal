import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { forgotPasswordSchema } from '$lib/forms/schemas/forgot-password-schema';

export const load = async () => {
	const form = await superValidate(zod4(forgotPasswordSchema));
	return { form };
};
