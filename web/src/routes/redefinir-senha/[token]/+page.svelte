<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import AppFooter from '$lib/components/app-footer.svelte';
	import { Button } from '$lib/components/ui/button';
	import SimpleInput from '$lib/components/forms/simple-input.svelte';
	import {
		resetPasswordSchema,
		type ResetPasswordData
	} from '$lib/forms/schemas/reset-password-schema';
	import { api } from '$lib/api-client';
	import { mensagemDeErro } from '$lib/utils/erros';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import { toast } from 'svelte-sonner';
	import { superForm } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	let erro = $state<string | null>(null);

	const form = superForm<ResetPasswordData>(data.form, {
		SPA: true,
		validators: zod4Client(resetPasswordSchema),
		resetForm: false,
		onSubmit: async ({ formData }) => {
			const { password } = Object.fromEntries(formData) as ResetPasswordData;
			erro = null;
			try {
				await api.post('auth/reset-password', { token: page.params.token, password });
				toast.success('Senha redefinida. Entre com a senha nova.');
				goto('/login');
			} catch (err) {
				// O link pode ter expirado entre abrir a página e enviar o formulário.
				erro = mensagemDeErro(err, 'Não foi possível redefinir a senha. Tente novamente.');
			}
		}
	});

	const { form: formData, enhance, delayed } = form;
</script>

<div
	class="flex min-h-screen flex-col bg-gradient-to-br from-primary via-accent via-70% to-secondary"
>
	<div class="flex flex-1 items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
		<div class="w-full max-w-md space-y-6 rounded-xl bg-white/80 p-8 shadow-lg backdrop-blur-md">
			{#if !data.tokenValido}
				<div class="space-y-4 text-center">
					<TriangleAlert class="mx-auto h-10 w-10 text-amber-600" />
					<h2 class="text-xl font-extrabold text-gray-900">Link inválido ou expirado</h2>
					<p class="text-sm text-gray-700">
						Este link já foi usado ou passou do prazo de validade. Peça um novo para redefinir a sua
						senha.
					</p>
					<a
						href="/esqueci-a-senha"
						class="inline-block text-sm font-medium text-primary hover:underline"
					>
						Pedir um novo link
					</a>
				</div>
			{:else}
				<div class="space-y-2">
					<h2 class="text-left text-xl font-extrabold text-gray-900">Escolha uma senha nova</h2>
					<p class="text-sm text-gray-700">A senha deve ter no mínimo 8 caracteres.</p>
				</div>

				{#if erro}
					<p class="rounded-lg bg-red-50 p-3 text-sm text-red-900">{erro}</p>
				{/if}

				<form method="POST" use:enhance class="space-y-6">
					<SimpleInput
						{form}
						name="password"
						type="password"
						label="Nova senha"
						bind:value={$formData.password}
						autocomplete="new-password"
					/>
					<SimpleInput
						{form}
						name="confirmPassword"
						type="password"
						label="Confirme a nova senha"
						bind:value={$formData.confirmPassword}
						autocomplete="new-password"
					/>
					<Button type="submit" class="h-12 w-full">
						{#if $delayed}
							<div class="flex items-center gap-2">
								<span>Salvando...</span>
								<LoaderCircle class="h-4 w-4 animate-spin" />
							</div>
						{:else}
							Redefinir senha
						{/if}
					</Button>
				</form>
			{/if}
		</div>
	</div>
	<AppFooter />
</div>
