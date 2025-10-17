<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import SimpleInput from '$lib/components/forms/simple-input.svelte';
	import {
		setupAdminSchema,
		type SetupAdminData
	} from '$lib/forms/schemas/setup-admin-schema';
	import { toast } from 'svelte-sonner';
	import { api } from '$lib/api-client';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import { superForm } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import type { PageData } from './$types';
	import AlertCircle from '@lucide/svelte/icons/alert-circle';

	let { data }: { data: PageData } = $props();

	// Initialize form with client-side validation
	const form = superForm<SetupAdminData>(data.form, {
		SPA: true,
		validators: zod4Client(setupAdminSchema),
		resetForm: false,
		onSubmit: async ({ formData }) => {
			const payload = Object.fromEntries(formData) as SetupAdminData;

			try {
				const response = await api.post('auth/setup-admin', payload);

				if (!response.ok) {
					const errorData = await response.json().catch(() => ({}));
					const errorMessage =
						errorData.error ||
						errorData.message ||
						'Erro ao configurar administrador';
					toast.error(errorMessage);
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

				toast.success('Administrador criado com sucesso!');
				goto('/');
			} catch (error) {
				console.error('Setup admin error:', error);
				toast.error('Erro ao configurar administrador. Por favor, tente novamente.');
			}
		}
	});

	const { form: formData, enhance, delayed } = form;
</script>

<div
	class="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary via-accent via-70% to-secondary px-4 py-12 sm:px-6 lg:px-8"
>
	<div class="w-full max-w-md space-y-8 rounded-xl bg-white/80 p-8 shadow-lg backdrop-blur-md">
		<div class="space-y-2">
			<h2 class="text-left text-xl font-extrabold text-gray-900">
				Configuração Inicial do Sistema
			</h2>
			<div class="flex items-start gap-2 rounded-lg bg-blue-50 p-3 text-sm text-blue-900">
				<AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
				<p>
					Este é o primeiro acesso ao sistema. Crie a conta de administrador para começar.
					O token de configuração pode ser obtido através do responsável pelo setup do sistema.
				</p>
			</div>
		</div>

		<form method="POST" use:enhance class="space-y-6">
			<SimpleInput
				{form}
				name="email"
				label="Email do Administrador"
				bind:value={$formData.email}
				autocomplete="email"
			/>
			<SimpleInput
				{form}
				name="password"
				type="password"
				label="Senha"
				bind:value={$formData.password}
				autocomplete="new-password"
			/>
			<SimpleInput
				{form}
				name="setup_token"
				type="password"
				label="Token de Configuração"
				bind:value={$formData.setup_token}
				autocomplete="off"
			/>
			<Button type="submit" class="h-12 w-full">
				{#if $delayed}
					<div class="flex items-center gap-2">
						<span>Criando...</span>
						<LoaderCircle class="h-4 w-4 animate-spin" />
					</div>
				{:else}
					Criar Administrador
				{/if}
			</Button>
		</form>
	</div>
</div>
