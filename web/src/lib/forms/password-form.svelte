<script lang="ts">
	import { superForm, type Infer, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { passwordChangeSchema, type PasswordChangeSchema } from './schemas/password-schema';
	import { Button } from '$lib/components/ui/button';
	import { SimpleInput } from '$lib/components/forms';
	import * as Card from '$lib/components/ui/card';
	import { api } from '$lib/api-client';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';

	let {
		data,
		isAdmin = false,
		isOwnProfile = false,
		userName = '',
		userEmail = '',
		userId,
		onError
	}: {
		data: SuperValidated<Infer<PasswordChangeSchema>>;
		isAdmin?: boolean;
		isOwnProfile?: boolean;
		userName?: string;
		userEmail?: string;
		userId: string | number;
		onError?: (error: any) => void;
	} = $props();

	const form = superForm(data, {
		SPA: true,
		validators: zod4Client(passwordChangeSchema),
		resetForm: false,
		onSubmit: async ({ formData }) => {
			const formValues = Object.fromEntries(formData);

			try {
				const response = await api.put(`user/${userId}/password`, {
					currentPassword: formValues.currentPassword,
					newPassword: formValues.newPassword,
					fromAdmin: isAdmin && !isOwnProfile
				});

				if (!response.ok) {
					const errorData = await response.json().catch(() => ({}));
					toast.error(errorData.message || 'Erro ao alterar senha');
					onError?.(errorData);
					return;
				}

				toast.success('Senha alterada com sucesso!');
				goto(`/usuarios/${userId}`);
			} catch (error) {
				console.error('Password change error:', error);
				toast.error('Erro ao alterar senha. Por favor, tente novamente.');
				onError?.(error);
			}
		}
	});

	const { form: formData, enhance } = form;

	const showCurrentPassword = $derived(!isAdmin || isOwnProfile);
</script>

<form method="POST" use:enhance class="space-y-6">
	<Card.Root>
		<Card.Header>
			<Card.Title>
				{isAdmin && !isOwnProfile ? 'Alterar Senha do Usuário' : 'Alterar Minha Senha'}
			</Card.Title>
			<Card.Description>
				{isAdmin && !isOwnProfile
					? `Alterando senha de ${userName} (${userEmail})`
					: 'Digite sua senha atual e a nova senha desejada'}
			</Card.Description>
		</Card.Header>
		<Card.Content class="space-y-4">
			{#if isAdmin && !isOwnProfile}
				<div class="rounded-md border border-blue-200 bg-blue-50 p-4">
					<p class="text-sm text-blue-800">
						Como administrador, você pode alterar a senha deste usuário sem conhecer a senha atual.
					</p>
				</div>
			{/if}

			{#if showCurrentPassword}
				<SimpleInput
					label="Senha Atual"
					name="currentPassword"
					{form}
					bind:value={$formData.currentPassword}
					placeholder="Digite sua senha atual"
					type="password"
					autocomplete="current-password"
				/>
			{/if}

			<div>
				<SimpleInput
					label="Nova Senha"
					name="newPassword"
					{form}
					bind:value={$formData.newPassword}
					placeholder="Digite a nova senha"
					type="password"
					autocomplete="new-password"
				/>
				<p class="mt-1 text-sm text-gray-600">A senha deve ter pelo menos 8 caracteres</p>
			</div>

			<SimpleInput
				label="Confirmar Nova Senha"
				name="confirmPassword"
				{form}
				bind:value={$formData.confirmPassword}
				placeholder="Confirme a nova senha"
				type="password"
				autocomplete="new-password"
			/>
		</Card.Content>
	</Card.Root>

	<div class="flex justify-end gap-4">
		<Button type="button" variant="outline" href={`/usuarios/${userId}`}>Cancelar</Button>
		<Button type="submit">Alterar Senha</Button>
	</div>
</form>
