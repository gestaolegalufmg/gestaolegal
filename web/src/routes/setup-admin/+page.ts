import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import { setupAdminSchema } from '$lib/forms/schemas/setup-admin-schema';

export const load = async () => {
	const form = await superValidate(zod4(setupAdminSchema));
	return { form };
};
