<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import {
		Card,
		CardContent,
		CardDescription,
		CardHeader,
		CardTitle
	} from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { superForm } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { goto } from '$app/navigation';
	import type { PageProps } from './$types';
	import { passwordChangeSchema } from '$lib/forms/schemas/password-schema';
	import { api } from '$lib/api-client';
	import { ApiException } from '$lib/types';
	import { toast } from 'svelte-sonner';

	let { data }: PageProps = $props();

	let formData = superForm(data.form, {
		SPA: true,
		validators: zod4Client(passwordChangeSchema),
		onSubmit: async ({ formData }) => {
			const formValues = Object.fromEntries(formData);

			try {
				await api.put(`user/${data.me.id}/password`, {
					currentPassword: formValues.currentPassword,
					newPassword: formValues.newPassword,
					fromAdmin: false
				});

				toast.success('Senha alterada com sucesso!');
				goto('/');
			} catch (err) {
				if (err instanceof ApiException) {
					toast.error(err.message);
				} else {
					toast.error('Erro ao alterar senha');
					console.error(err);
				}
			}
		}
	});

	let { form: formValues, enhance, errors } = formData;
</script>

<div class="container mx-auto max-w-2xl py-6">
	<Card>
		<CardHeader>
			<CardTitle>Alterar Minha Senha</CardTitle>
			<CardDescription>Digite sua senha atual e a nova senha desejada</CardDescription>
		</CardHeader>
		<CardContent>
			<form method="POST" use:enhance>
				<div class="space-y-4">
					<div class="space-y-2">
						<Label for="currentPassword">Senha Atual</Label>
						<Input
							id="currentPassword"
							name="currentPassword"
							type="password"
							bind:value={$formValues.currentPassword}
							placeholder="Digite sua senha atual"
						/>
						{#if $errors.currentPassword}
							<p class="text-sm text-red-600">{$errors.currentPassword}</p>
						{/if}
					</div>

					<div class="space-y-2">
						<Label for="newPassword">Nova Senha</Label>
						<Input
							id="newPassword"
							name="newPassword"
							type="password"
							bind:value={$formValues.newPassword}
							placeholder="Digite a nova senha"
						/>
						{#if $errors.newPassword}
							<p class="text-sm text-red-600">{$errors.newPassword}</p>
						{/if}
						<p class="text-sm text-gray-600">A senha deve ter pelo menos 8 caracteres</p>
					</div>

					<div class="space-y-2">
						<Label for="confirmPassword">Confirmar Nova Senha</Label>
						<Input
							id="confirmPassword"
							name="confirmPassword"
							type="password"
							bind:value={$formValues.confirmPassword}
							placeholder="Confirme a nova senha"
						/>
						{#if $errors.confirmPassword}
							<p class="text-sm text-red-600">{$errors.confirmPassword}</p>
						{/if}
					</div>

					<div class="flex gap-2 pt-4">
						<Button type="submit" class="flex-1">Alterar Senha</Button>
						<Button type="button" variant="outline" href={`/usuarios/eu`}>Cancelar</Button>
					</div>
				</div>
			</form>
		</CardContent>
	</Card>
</div>
