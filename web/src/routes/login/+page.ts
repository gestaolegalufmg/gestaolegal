import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { loginSchema } from '$lib/forms/schemas/login-schema';

export const load = async () => {
	const form = await superValidate(zod4(loginSchema));
	return { form };
};
