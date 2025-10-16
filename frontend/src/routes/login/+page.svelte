<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { Button } from '$lib/components/ui/button';
	import SimpleInput from '$lib/components/forms/simple-input.svelte';
	import { loginSchema, type LoginData } from '$lib/forms/schemas/login-schema';
	import { toast } from 'svelte-sonner';
	import { api } from '$lib/api-client';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import { superForm } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';

	// Initialize form with client-side validation
	const form = superForm<LoginData>(
		{ email: '', password: '' },
		{
			SPA: true,
			validators: zod4Client(loginSchema),
			resetForm: false,

			onSubmit: async ({ formData }) => {
				const data = Object.fromEntries(formData) as LoginData;

				try {
					const response = await api.post('auth/login', data);

					if (!response.ok) {
						const errorData = await response.json().catch(() => ({}));
						toast.error(errorData.message || 'Credenciais inválidas');
						return;
					}

					// Backend will set httpOnly cookie via Set-Cookie header
					toast.success('Login realizado com sucesso!');

					// Redirect to dashboard or requested page
					const redirectTo = $page.url.searchParams.get('redirectTo') || '/';
					goto(redirectTo);
				} catch (error) {
					console.error('Login error:', error);
					toast.error('Erro ao fazer login. Por favor, tente novamente.');
				}
			}
		}
	);

	const { form: formData, enhance, delayed } = form;
</script>

<div
	class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-primary via-accent via-70% to-secondary"
>
	<div class="max-w-md w-full space-y-8 bg-white/80 rounded-xl shadow-lg p-8 backdrop-blur-md">
		<h2 class="text-left text-xl font-extrabold text-gray-900">Login no Gestao Legal</h2>

		<form method="POST" use:enhance class="space-y-8">
			<SimpleInput
				{form}
				name="email"
				label="Email"
				bind:value={$formData.email}
				autocomplete="email"
			/>
			<SimpleInput
				{form}
				name="password"
				type="password"
				label="Senha"
				bind:value={$formData.password}
				autocomplete="current-password"
			/>
			<Button type="submit" class="w-full h-12">
				{#if $delayed}
					<div class="flex items-center gap-2">
						<span>Carregando...</span>
						<LoaderCircle class="w-4 h-4 animate-spin" />
					</div>
				{:else}
					Entrar
				{/if}
			</Button>
		</form>
	</div>
</div>
