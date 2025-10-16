import { passwordChangeSchema } from '$lib/forms/schemas/password-schema';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	const form = await superValidate(zod4(passwordChangeSchema));

	return {
		form
	};
};
