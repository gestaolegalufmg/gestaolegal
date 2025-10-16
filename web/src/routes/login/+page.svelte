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
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	// Initialize form with client-side validation
	const form = superForm<LoginData>(data.form, {
		SPA: true,
		validators: zod4Client(loginSchema),
		resetForm: false,
		onSubmit: async ({ formData }) => {
			const payload = Object.fromEntries(formData) as LoginData;

			try {
				const response = await api.post('auth/login', payload);

				if (!response.ok) {
					const errorData = await response.json().catch(() => ({}));
					toast.error(errorData.message || 'Credenciais inválidas');
					return;
				}

				const responseData = await response.json();
				if (responseData?.token && typeof document !== 'undefined') {
					const maxAge = 60 * 60 * 8; // 8 hours
					const secureFlag =
						typeof window !== 'undefined' && window.location.protocol === 'https:'
							? '; Secure'
							: '';
					document.cookie = `auth_token=${responseData.token}; Path=/; Max-Age=${maxAge}; SameSite=Strict${secureFlag}`;
				}

				toast.success('Login realizado com sucesso!');

				const redirectTo = $page.url.searchParams.get('redirectTo') || '/';
				goto(redirectTo);
			} catch (error) {
				console.error('Login error:', error);
				toast.error('Erro ao fazer login. Por favor, tente novamente.');
			}
		}
	});

	const { form: formData, enhance, delayed } = form;
</script>

<div
	class="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary via-accent via-70% to-secondary px-4 py-12 sm:px-6 lg:px-8"
>
	<div class="w-full max-w-md space-y-8 rounded-xl bg-white/80 p-8 shadow-lg backdrop-blur-md">
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
			<Button type="submit" class="h-12 w-full">
				{#if $delayed}
					<div class="flex items-center gap-2">
						<span>Carregando...</span>
						<LoaderCircle class="h-4 w-4 animate-spin" />
					</div>
				{:else}
					Entrar
				{/if}
			</Button>
		</form>
	</div>
</div>
