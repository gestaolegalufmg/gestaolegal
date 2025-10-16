<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import type { PageProps } from './$types';
	import { TIPO_EVENTO_OPTIONS } from '$lib/constants/tipo_evento';
	import { superForm } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import { eventoUpdateFormSchema } from '$lib/forms/schemas/evento-schema';
	import {
		SimpleDatePicker,
		SimpleInput,
		SimpleSelect,
		SimpleTextArea
	} from '$lib/components/forms';
	import { fileProxy } from 'sveltekit-superforms';
	import { toast } from 'svelte-sonner';
	import FileText from '@lucide/svelte/icons/file-text';
	import Download from '@lucide/svelte/icons/download';
	import UsuarioSelectorDialog from '$lib/components/usuario-selector-dialog.svelte';
	import type { User } from '$lib/types';
	import UserPlus from '@lucide/svelte/icons/user-plus';
	import X from '@lucide/svelte/icons/x';
	import { apiFetch, api } from '$lib/api-client';
	import { goto } from '$app/navigation';

	let { data }: PageProps = $props();
	const { evento, caso, form: initialForm } = data;

	let fileInputValue = $state('');

	const form = superForm(initialForm, {
		SPA: true,
		validators: zod4Client(eventoUpdateFormSchema),
		resetForm: false,
		onSubmit: async ({ formData }) => {
			try {
				const submission = new FormData();

				const tipo = formData.get('tipo');
				if (typeof tipo === 'string') {
					submission.append('tipo', tipo);
				}

				const dataEvento = formData.get('data_evento');
				if (typeof dataEvento === 'string') {
					submission.append('data_evento', dataEvento);
				}

				const status = formData.get('status');
				if (status !== null) {
					submission.append('status', status.toString());
				}

				const descricao = formData.get('descricao');
				if (typeof descricao === 'string' && descricao.trim() !== '') {
					submission.append('descricao', descricao);
				}

				const responsavel = formData.get('id_usuario_responsavel');
				if (typeof responsavel === 'string' && responsavel !== '') {
					submission.append('id_usuario_responsavel', responsavel);
				}

				const arquivo = formData.get('arquivo');
				if (arquivo instanceof File && arquivo.size > 0) {
					submission.append('arquivo', arquivo);
				}

				const response = await apiFetch(`caso/${caso.id}/eventos/${evento.id}`, {
					method: 'PUT',
					body: submission,
					headers: {}
				});

				if (!response.ok) {
					const errorData = await response.json().catch(() => ({}));
					toast.error(errorData.message || 'Erro ao atualizar evento');
					return;
				}

				toast.success('Evento atualizado com sucesso!');
				goto(`/casos/${caso.id}/eventos/${evento.id}`);
			} catch (error) {
				console.error('Evento update error:', error);
				toast.error('Erro ao atualizar evento. Por favor, tente novamente.');
			}
		}
	});

	const { form: formData, enhance } = form;

	const eventoFile = fileProxy(form, 'arquivo');

	let selectedUsuario = $state<User | null>(evento.usuario_responsavel || null);

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

	// $effect(() => {
	// 	if (evento.usuario_responsavel) {
	// 		selectedUsuario = evento.usuario_responsavel;
	// 	}
	// });

	async function handleDownload() {
		if (!evento.arquivo) return;

		const response = await api.get(`caso/${caso.id}/eventos/${evento.id}/download`);
		if (!response.ok) {
			toast.error('Erro ao baixar arquivo');
			return;
		}

		const blob = await response.blob();
		const url = window.URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = evento.arquivo.split('/').pop() || 'arquivo';
		document.body.appendChild(a);
		a.click();
		window.URL.revokeObjectURL(url);
		document.body.removeChild(a);
	}

	function getTipoLabel(tipo: string) {
		const option = TIPO_EVENTO_OPTIONS.find((opt) => opt.value === tipo);
		return option?.label || tipo;
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold tracking-tight">
				Editar Evento #{evento.num_evento || evento.id}
			</h1>
			<p class="text-muted-foreground">
				<a href="/casos/{caso.id}" class="hover:underline">Caso #{caso.id}</a>
				/ {getTipoLabel(evento.tipo)}
			</p>
		</div>
		<Button variant="outline" href="/casos/{caso.id}/eventos/{evento.id}">Voltar</Button>
	</div>

	<Card.Root>
		<Card.Header>
			<Card.Title>Editar Evento</Card.Title>
		</Card.Header>
		<Card.Content>
			<form method="POST" enctype="multipart/form-data" use:enhance class="space-y-6">
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
					label="Data do Evento"
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

				<div class="space-y-2">
					<SimpleInput
						label="Arquivo"
						name="arquivo"
						{form}
						bind:files={$eventoFile}
						bind:value={fileInputValue}
						type="file"
					/>
					{#if evento.arquivo}
						<div class="flex items-center justify-between rounded-lg bg-muted/50 p-3">
							<div class="flex items-center gap-2">
								<FileText class="h-5 w-5" />
								<span class="text-sm">Arquivo atual: {evento.arquivo.split('/').pop()}</span>
							</div>
							<Button variant="ghost" size="sm" onclick={handleDownload}>
								<Download class="h-4 w-4" />
							</Button>
						</div>
					{/if}
				</div>

				<div class="flex justify-end gap-2">
					<Button type="button" variant="outline" href="/casos/{caso.id}/eventos/{evento.id}">
						Cancelar
					</Button>
					<Button type="submit">Salvar Alterações</Button>
				</div>
			</form>
		</Card.Content>
	</Card.Root>
</div>
