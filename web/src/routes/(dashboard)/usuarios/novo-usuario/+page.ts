import { userCreateFormSchema } from '$lib/forms/schemas/user-schema';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';

export const load = async () => {
	const form = await superValidate(zod4(userCreateFormSchema));
	return { form };
};
