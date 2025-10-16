<script lang="ts">
	import LoginForm from '$lib/forms/login-form.svelte';
	import { superForm } from 'sveltekit-superforms';
	import type { PageProps } from './$types';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { loginSchema } from '$lib/forms/schemas/login-schema';
	import { toast } from 'svelte-sonner';

	let { data }: PageProps = $props();

	let { form: formData } = data;

	const form = superForm(formData, {
		validators: zod4Client(loginSchema),
		resetForm: false,
		delayMs: 200,

		onError: ({ result }) => {
			if (result.error.message) {
				toast.error(`Erro ao fazer login: ${result.error.message}`);
			} else {
				toast.error('Erro ao fazer login. Por favor, tente novamente.');
			}
		}
	});
</script>

<div
	class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-primary via-accent via-70% to-secondary"
>
	<div class="max-w-md w-full space-y-8 bg-white/80 rounded-xl shadow-lg p-8 backdrop-blur-md">
		<h2 class="text-left text-xl font-extrabold text-gray-900">Login no Gestao Legal</h2>
		<LoginForm {form} />
	</div>
</div>
