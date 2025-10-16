<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { fileProxy, superForm, type SuperValidated } from 'sveltekit-superforms';
	import type { Infer } from 'sveltekit-superforms';
	import {
		eventoCreateFormSchema,
		type EventoCreateFormSchema
	} from '$lib/forms/schemas/evento-schema';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { SimpleDatePicker, SimpleInput, SimpleSelect, SimpleTextArea } from './forms';
	import { TIPO_EVENTO_OPTIONS } from '$lib/constants/tipo_evento';
	import { Button } from './ui/button';
	import UsuarioSelectorDialog from './usuario-selector-dialog.svelte';
	import type { User } from '$lib/types';
	import UserPlus from '@lucide/svelte/icons/user-plus';
	import X from '@lucide/svelte/icons/x';
	import { apiFetch } from '$lib/api-client';
	import { toast } from 'svelte-sonner';
	import { page } from '$app/stores';

	let {
		open = $bindable(false),
		onSuccess = async () => {},
		eventoFormData
	}: {
		open: boolean;
		onSuccess?: () => Promise<void>;
		eventoFormData: SuperValidated<Infer<EventoCreateFormSchema>>;
	} = $props();

	const form = superForm(eventoFormData, {
		SPA: true,
		validators: zod4Client(eventoCreateFormSchema),
		resetForm: false,
		onSubmit: async ({ formData }) => {
			try {
				const casoId = $page.params.id;

				// Create FormData for multipart upload
				const data = new FormData();
				for (const [key, value] of formData.entries()) {
					if (value !== null && value !== undefined) {
						data.append(key, value);
					}
				}

				const response = await apiFetch(`caso/${casoId}/eventos`, {
					method: 'POST',
					body: data,
					headers: {}
				});

				if (!response.ok) {
					const errorData = await response.json().catch(() => ({}));
					toast.error(errorData.message || 'Erro ao criar evento');
					return;
				}

				toast.success('Evento criado com sucesso!');
				open = false;
				await onSuccess();
			} catch (error) {
				console.error('Evento creation error:', error);
				toast.error('Erro ao criar evento. Por favor, tente novamente.');
			}
		}
	});

	const { form: formData, enhance } = form;

	let value = $state('');
	const eventoFile = fileProxy(form, 'arquivo');

	let selectedUsuario = $state<User | null>(null);

	function handleUsuarioSelected(usuario: User | null) {
		selectedUsuario = usuario;
		if (usuario) {
			$formData.id_usuario_responsavel = usuario.id;
		} else {
			$formData.id_usuario_responsavel = null;
		}
	}

	function removeUsuario() {
		selectedUsuario = null;
		$formData.id_usuario_responsavel = null;
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="max-h-[90vh] overflow-y-auto sm:max-w-[70vw]">
		<Dialog.Header>
			<Dialog.Title>Novo Evento</Dialog.Title>
			<Dialog.Description>Adicione um novo evento ao caso.</Dialog.Description>
		</Dialog.Header>

		<div class="py-4">
			<form class="space-y-6" use:enhance method="POST" enctype="multipart/form-data">
				<SimpleSelect
					label="Tipo de Evento"
					name="tipo"
					{form}
					bind:value={$formData.tipo}
					options={TIPO_EVENTO_OPTIONS}
				/>
				<SimpleTextArea
					label="Descrição"
					name="descricao"
					{form}
					bind:value={$formData.descricao}
				/>
				<SimpleDatePicker
					label="Data do Ocorrido"
					placeholder="Selecione a data"
					name="data_evento"
					{form}
					bind:value={$formData.data_evento}
				/>

				<div class="space-y-2">
					<p class="text-sm font-medium">Usuário Responsável</p>
					<UsuarioSelectorDialog
						{form}
						name="id_usuario_responsavel"
						bind:selectedUsuarioId={$formData.id_usuario_responsavel}
						onSelect={handleUsuarioSelected}
					>
						{#snippet trigger()}
							<UserPlus class="mr-2 h-4 w-4" />
							Selecionar Usuário
						{/snippet}
					</UsuarioSelectorDialog>

					{#if selectedUsuario}
						<div class="flex items-center justify-between rounded-lg bg-muted/50 p-3">
							<div class="min-w-0 flex-1">
								<p class="truncate text-sm font-medium">{selectedUsuario.nome}</p>
								<div class="flex gap-4 text-xs text-muted-foreground">
									<span>{selectedUsuario.email}</span>
								</div>
							</div>
							<Button
								variant="ghost"
								size="sm"
								class="h-8 w-8 p-0 hover:bg-transparent"
								onclick={removeUsuario}
								type="button"
							>
								<X class="h-3 w-3" />
							</Button>
						</div>
					{/if}
				</div>

				<SimpleInput
					label="Arquivo"
					name="arquivo"
					{form}
					bind:files={$eventoFile}
					bind:value
					type="file"
				/>

				<div class="flex justify-end gap-2">
					<Button variant="outline" onclick={() => (open = false)}>Cancelar</Button>
					<Button type="submit">Criar Evento</Button>
				</div>
			</form>
		</div>
	</Dialog.Content>
</Dialog.Root>
