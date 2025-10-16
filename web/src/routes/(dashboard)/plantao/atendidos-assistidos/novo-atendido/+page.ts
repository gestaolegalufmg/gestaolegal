import { atendidoCreateFormSchema } from '$lib/forms/schemas/atendido-schema';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';

export const load = async () => {
	const form = await superValidate(zod4(atendidoCreateFormSchema));
	return { form };
};
