<script lang="ts">
	import AppFooter from '$lib/components/app-footer.svelte';
	import { Button } from '$lib/components/ui/button';
	import SimpleInput from '$lib/components/forms/simple-input.svelte';
	import {
		forgotPasswordSchema,
		type ForgotPasswordData
	} from '$lib/forms/schemas/forgot-password-schema';
	import { api } from '$lib/api-client';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import MailCheck from '@lucide/svelte/icons/mail-check';
	import { superForm } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	/** Confirmação exibida no lugar do formulário depois do pedido. */
	let enviado = $state(false);
	let erro = $state<string | null>(null);

	const form = superForm<ForgotPasswordData>(data.form, {
		SPA: true,
		validators: zod4Client(forgotPasswordSchema),
		resetForm: false,
		// onUpdate, não onSubmit: este roda antes da validação e enviaria o
		// formulário mesmo com o e-mail inválido.
		onUpdate: async ({ form: validado, result }) => {
			erro = null;
			if (result.type === 'failure' || !validado.valid) {
				return;
			}
			try {
				await api.post('auth/forgot-password', { email: validado.data.email });
				// A API responde igual exista ou não a conta, para não revelar
				// quem tem cadastro; a tela segue a mesma linha.
				enviado = true;
			} catch {
				erro = 'Não foi possível concluir o pedido. Tente novamente em instantes.';
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
			{#if enviado}
				<div class="space-y-4 text-center">
					<MailCheck class="mx-auto h-10 w-10 text-primary" />
					<h2 class="text-xl font-extrabold text-gray-900">Verifique seu e-mail</h2>
					<p class="text-sm text-gray-700">
						Se este e-mail estiver cadastrado, enviamos as instruções para redefinir a senha. O link
						vale por uma hora.
					</p>
					<a href="/login" class="inline-block text-sm font-medium text-primary hover:underline">
						Voltar para o login
					</a>
				</div>
			{:else}
				<div class="space-y-2">
					<h2 class="text-left text-xl font-extrabold text-gray-900">Esqueci minha senha</h2>
					<p class="text-sm text-gray-700">
						Informe o e-mail cadastrado no sistema. Enviaremos um link para você escolher uma senha
						nova.
					</p>
				</div>

				{#if erro}
					<p class="rounded-lg bg-red-50 p-3 text-sm text-red-900">{erro}</p>
				{/if}

				<form method="POST" use:enhance class="space-y-6">
					<SimpleInput
						{form}
						name="email"
						label="Email"
						bind:value={$formData.email}
						autocomplete="email"
					/>
					<Button type="submit" class="h-12 w-full">
						{#if $delayed}
							<div class="flex items-center gap-2">
								<span>Enviando...</span>
								<LoaderCircle class="h-4 w-4 animate-spin" />
							</div>
						{:else}
							Enviar link de redefinição
						{/if}
					</Button>
				</form>

				<p class="text-center text-sm text-gray-600">
					<a href="/login" class="font-medium text-primary hover:underline">Voltar para o login</a>
				</p>
			{/if}
		</div>
	</div>
	<AppFooter />
</div>
