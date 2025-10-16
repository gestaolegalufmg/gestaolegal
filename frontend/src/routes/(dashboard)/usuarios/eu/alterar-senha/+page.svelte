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
	import { z } from 'zod';
	import { goto } from '$app/navigation';
	import type { PageProps } from './$types';

	const passwordSchema = z
		.object({
			currentPassword: z.string().min(1, 'Senha atual é obrigatória'),
			newPassword: z.string().min(8, 'Nova senha deve ter pelo menos 8 caracteres'),
			confirmPassword: z.string().min(1, 'Confirmação de senha é obrigatória')
		})
		.refine((data) => data.newPassword === data.confirmPassword, {
			message: 'As senhas não coincidem',
			path: ['confirmPassword']
		});

	let { data }: PageProps = $props();

	let formData = superForm(data.form, {
		validators: zod4Client(passwordSchema),
		onSubmit: async ({ formData }) => {
			const response = await fetch(`/api/user/me/password`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(formData)
			});

			if (response.ok) {
				await goto('/');
			}
		}
	});

	let { form: formValues, enhance, errors } = formData;
</script>

<div class="container mx-auto py-6 max-w-2xl">
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
