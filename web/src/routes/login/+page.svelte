<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import SimpleInput from '$lib/components/forms/simple-input.svelte';
	import { loginSchema, type LoginData } from '$lib/forms/schemas/login-schema';
	import { toast } from 'svelte-sonner';
	import { api } from '$lib/api-client';
	import { ApiException } from '$lib/types';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import { superForm } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import type { PageData } from './$types';
	import { page } from '$app/state';

	let { data }: { data: PageData } = $props();

	/** Aviso exibido junto ao formulário quando o login não é aceito. */
	let erroLogin = $state<string | null>(null);

	const form = superForm<LoginData>(data.form, {
		SPA: true,
		validators: zod4Client(loginSchema),
		resetForm: false,
		onSubmit: async ({ formData }) => {
			const payload = Object.fromEntries(formData) as LoginData;
			erroLogin = null;

			try {
				const responseData = await api.post<{ token: string; user: any }>('auth/login', payload);

				if (responseData?.token && typeof document !== 'undefined') {
					const maxAge = 60 * 60 * 8; // 8 hours
					const secureFlag =
						typeof window !== 'undefined' && window.location.protocol === 'https:'
							? '; Secure'
							: '';
					document.cookie = `auth_token=${responseData.token}; Path=/; Max-Age=${maxAge}; SameSite=Strict${secureFlag}`;
				}

				toast.success('Login realizado com sucesso!');

				const redirectTo = page.url.searchParams.get('redirectTo') || '/';
				goto(redirectTo);
			} catch (err) {
				if (err instanceof ApiException) {
					// 401 = e-mail não cadastrado ou senha incorreta. A API não
					// diferencia os dois casos de propósito, para não permitir
					// descobrir quais e-mails existem.
					erroLogin =
						err.statusCode === 401
							? data.needsSetup
								? 'Nenhum usuário cadastrado ainda. Configure o administrador para acessar o sistema.'
								: 'E-mail ou senha incorretos. Verifique os dados e tente novamente.'
							: err.message;
				} else {
					console.error('Login error:', err);
					erroLogin = 'Não foi possível conectar ao servidor. Tente novamente em instantes.';
				}
				toast.error(erroLogin);
			}
		}
	});

	const { form: formData, enhance, delayed } = form;
</script>

<div
	class="from-primary via-accent to-secondary flex min-h-screen items-center justify-center bg-gradient-to-br via-70% px-4 py-12 sm:px-6 lg:px-8"
>
	<div class="w-full max-w-md space-y-6">
		<img
			src="/logo-gestao-legal.png"
			alt="Gestão Legal"
			class="mx-auto w-96 max-w-full drop-shadow-lg"
		/>

		<div class="space-y-8 rounded-xl bg-white/80 p-8 shadow-lg backdrop-blur-md">
			<!-- O nome do sistema já aparece no logo acima; aqui basta a ação. -->
			<h2 class="text-center text-xl font-extrabold text-gray-900">Acesse sua conta</h2>

			{#if erroLogin}
				<div
					role="alert"
					aria-live="assertive"
					class="border-destructive/40 bg-destructive/10 text-destructive flex items-start gap-2 rounded-md border p-3 text-sm"
				>
					<TriangleAlert class="mt-0.5 h-4 w-4 shrink-0" />
					<div class="space-y-1">
						<p>{erroLogin}</p>
						{#if data.needsSetup}
							<a href="/setup-admin" class="font-medium underline">Configurar administrador</a>
						{/if}
					</div>
				</div>
			{/if}

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

			{#if data.needsSetup}
				<div class="mt-4 text-center text-sm text-gray-600">
					<p class="cursor-default">
						Primeiro acesso?
						<a href="/setup-admin" class="text-primary font-medium hover:underline">
							Configure o administrador
						</a>
					</p>
				</div>
			{/if}
		</div>
	</div>
</div>
