<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import { Button } from '$lib/components/ui/button';
	import { FormSection, SimpleSelect, SimpleTextArea } from '$lib/components/forms';
	import { casoCreateFormSchema } from './schemas/caso-schema';
	import { intProxy, superForm, type Infer, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import {
		AREA_DIREITO,
		AREA_DIREITO_OPTIONS,
		SUB_AREA_DIREITO_ADMINISTRATIVO_OPTIONS,
		SUB_AREA_DIREITO_CIVEL_OPTIONS
	} from '$lib/constants/area_direito';
	import { SITUACAO_DEFERIMENTO_OPTIONS } from '$lib/constants/situacao-deferimento';
	import type { User, Atendido } from '$lib/types';
	import AssistidoSelectorDialog from '$lib/components/assistido-selector-dialog.svelte';
	import { Badge } from '$lib/components/ui/badge';
	import X from '@lucide/svelte/icons/x';
	import UserPlus from '@lucide/svelte/icons/user-plus';
	import UploadIcon from '@lucide/svelte/icons/upload';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import { api } from '$lib/api-client';
	import { ApiException } from '$lib/types';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import { get } from 'svelte/store';
	import type { Caso } from '$lib/types';

	let {
		data,
		onUpdate,
		onError,
		isCreateMode = false,
		casoId,
		currentUserId,
		usuarios = [],
		assistidos = []
	}: {
		data: SuperValidated<Infer<typeof casoCreateFormSchema>>;
		isCreateMode?: boolean;
		casoId?: number;
		currentUserId?: number;
		onUpdate?: (data: any) => void;
		onError?: (error: any) => void;
		usuarios?: User[];
		assistidos?: Atendido[];
	} = $props();

	// PDF attachments are only collected while creating a new caso; they are
	// uploaded to the caso's /arquivos endpoint right after it is created.
	const MAX_ARQUIVO_BYTES = 10 * 1024 * 1024; // 10 MB
	let selectedFiles = $state<File[]>([]);
	let fileInput = $state<HTMLInputElement | null>(null);

	function handleFilesSelected(event: Event) {
		const target = event.target as HTMLInputElement;
		const files = Array.from(target.files ?? []);

		for (const file of files) {
			const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
			if (!isPdf) {
				toast.error(`"${file.name}" não é um PDF. Apenas arquivos .pdf são permitidos.`);
				continue;
			}
			if (file.size > MAX_ARQUIVO_BYTES) {
				toast.error(`"${file.name}" excede o tamanho máximo de 10 MB.`);
				continue;
			}
			if (!selectedFiles.some((f) => f.name === file.name && f.size === file.size)) {
				selectedFiles = [...selectedFiles, file];
			}
		}

		// Reset the input so the same file can be re-selected if removed.
		target.value = '';
	}

	function removeFile(index: number) {
		selectedFiles = selectedFiles.filter((_, i) => i !== index);
	}

	async function uploadArquivos(newCasoId: number) {
		for (const file of selectedFiles) {
			const fd = new FormData();
			fd.append('arquivo', file);
			try {
				await api.post(`caso/${newCasoId}/arquivos`, fd, { headers: {} });
			} catch (err) {
				const msg = err instanceof ApiException ? err.message : `Erro ao enviar "${file.name}"`;
				toast.error(msg);
			}
		}
	}

	const casoForm = superForm(data, {
		SPA: true,
		dataType: 'json',
		validators: zod4Client(casoCreateFormSchema),
		resetForm: false,
		taintedMessage: 'Tem certeza que deseja sair? Você perderá qualquer alteração não salva.',
		onUpdate: async ({ form, result }) => {
			try {
				if (result.type === 'failure') {
					toast.error('Por favor resolva os erros de preenchimento');
					return;
				}

				const responseData = isCreateMode
					? await api.post<Caso>('caso', form.data)
					: await api.put<Caso>(`caso/${casoId}`, form.data);

				if (isCreateMode && selectedFiles.length > 0) {
					await uploadArquivos(responseData.id);
				}

				toast.success(isCreateMode ? 'Caso criado com sucesso!' : 'Caso atualizado com sucesso!');

				// Use custom onUpdate callback if provided
				if (onUpdate) {
					onUpdate(responseData);
				} else {
					// invalidateAll so the destination view reloads fresh data instead of
					// showing the pre-edit values from SvelteKit's cached load.
					await goto(`/casos/${responseData.id}`, { invalidateAll: true });
				}
			} catch (err) {
				if (err instanceof ApiException) {
					toast.error(err.message);
					onError?.(err);
				} else {
					console.error('Caso form error:', err);
					toast.error('Erro ao salvar caso. Por favor, tente novamente.');
					onError?.(err);
				}
			}
		}
	});

	const { form: formData, enhance } = casoForm;

	const usuariosOptions = $derived(
		usuarios.map((u) => ({ value: u.id.toString(), label: u.nome }))
	);

	const usuarioProxy = intProxy(formData, 'id_usuario_responsavel');
	// Optional user selects bind to string values from the <select>; without a
	// proxy the string would fail the numeric zod schema with "invalid input".
	const orientadorProxy = intProxy(formData, 'id_orientador', { empty: 'null' });
	const estagiarioProxy = intProxy(formData, 'id_estagiario', { empty: 'null' });
	const colaboradorProxy = intProxy(formData, 'id_colaborador', { empty: 'null' });

	// On a new caso the responsible user is the logged-in user (field hidden),
	// and the deferral status defaults to "aguardando deferimento".
	if (isCreateMode) {
		if (currentUserId) {
			$formData.id_usuario_responsavel = currentUserId;
		}
		if (!$formData.situacao_deferimento) {
			$formData.situacao_deferimento = 'aguardando_deferimento';
		}
	}

	let selectedAssistidos = $state<Atendido[]>(assistidos || []);

	function handleAssistidosSelected(newAssistidos: Atendido[]) {
		selectedAssistidos = newAssistidos;
		$formData.ids_clientes = newAssistidos.map((a) => a.id);
	}

	function removeAssistido(assistidoId: number) {
		selectedAssistidos = selectedAssistidos.filter((a) => a.id !== assistidoId);
		$formData.ids_clientes = selectedAssistidos.map((a) => a.id);
	}
</script>

<form method="POST" use:enhance class="space-y-8">
	<FormSection title="Dados do Caso" description="Informações principais sobre o caso" columns="2">
		<SimpleSelect
			label="Área do Direito"
			name="area_direito"
			form={casoForm}
			bind:value={$formData.area_direito}
			options={AREA_DIREITO_OPTIONS}
			placeholder="Selecione a área do direito"
		/>

		{#if $formData.area_direito === AREA_DIREITO.ADMINISTRATIVO}
			<SimpleSelect
				label="Sub-área"
				name="sub_area"
				form={casoForm}
				bind:value={$formData.sub_area}
				options={SUB_AREA_DIREITO_ADMINISTRATIVO_OPTIONS}
			/>
		{/if}
		{#if $formData.area_direito === AREA_DIREITO.CIVEL}
			<SimpleSelect
				label="Sub-área"
				name="sub_area"
				form={casoForm}
				bind:value={$formData.sub_area}
				options={SUB_AREA_DIREITO_CIVEL_OPTIONS}
			/>
		{/if}

		{#if !isCreateMode}
			<SimpleSelect
				label="Situação do Deferimento"
				name="situacao_deferimento"
				form={casoForm}
				bind:value={$formData.situacao_deferimento}
				options={SITUACAO_DEFERIMENTO_OPTIONS}
				placeholder="Selecione a situação"
			/>
		{/if}
	</FormSection>

	<FormSection title="Assistidos" description="Selecione os assistidos para este caso" columns="1">
		<div class="space-y-4">
			<AssistidoSelectorDialog
				form={casoForm}
				name="ids_clientes"
				bind:selectedAssistidosIds={$formData.ids_clientes}
				onSelect={handleAssistidosSelected}
			>
				{#snippet trigger()}
					<UserPlus class="mr-2 h-4 w-4" />
					Adicionar Assistidos
				{/snippet}
			</AssistidoSelectorDialog>

			{#if selectedAssistidos.length > 0}
				<div class="space-y-2">
					<p class="text-sm font-medium">
						{selectedAssistidos.length} assistido(s) selecionado(s):
					</p>
					<div class="flex flex-wrap gap-2">
						{#each selectedAssistidos as assistido (assistido.id)}
							<Badge variant="secondary" class="py-1 pr-1 pl-3">
								<span class="mr-2">{assistido.nome}</span>
								<Button
									variant="ghost"
									size="sm"
									class="h-4 w-4 p-0 hover:bg-transparent"
									onclick={() => removeAssistido(assistido.id)}
									type="button"
								>
									<X class="h-3 w-3" />
								</Button>
							</Badge>
						{/each}
					</div>
				</div>
			{:else}
				<p class="text-sm text-muted-foreground">Nenhum assistido selecionado</p>
			{/if}
		</div>
	</FormSection>

	<FormSection title="Responsáveis" description="Defina os responsáveis pelo caso" columns="2">
		{#if !isCreateMode}
			<SimpleSelect
				label="Usuário Responsável"
				name="id_usuario_responsavel"
				form={casoForm}
				bind:value={$usuarioProxy}
				options={usuariosOptions}
				placeholder="Selecione o responsável"
			/>
		{/if}

		<SimpleSelect
			label="Orientador"
			name="id_orientador"
			form={casoForm}
			bind:value={$orientadorProxy}
			options={usuariosOptions}
			placeholder="Selecione o orientador (opcional)"
		/>

		<SimpleSelect
			label="Estagiário"
			name="id_estagiario"
			form={casoForm}
			bind:value={$estagiarioProxy}
			options={usuariosOptions}
			placeholder="Selecione o estagiário (opcional)"
		/>

		<SimpleSelect
			label="Colaborador"
			name="id_colaborador"
			form={casoForm}
			bind:value={$colaboradorProxy}
			options={usuariosOptions}
			placeholder="Selecione o colaborador (opcional)"
		/>
	</FormSection>

	<FormSection title="Detalhes" description="Informações adicionais do caso" columns="1">
		<SimpleTextArea
			label="Descrição"
			name="descricao"
			form={casoForm}
			bind:value={$formData.descricao}
			placeholder="Descreva o caso..."
			rows={5}
		/>

		{#if $formData.situacao_deferimento === 'indeferido'}
			<SimpleTextArea
				label="Justificativa de Indeferimento"
				name="justif_indeferimento"
				form={casoForm}
				bind:value={$formData.justif_indeferimento}
				placeholder="Justificativa (se aplicável)..."
				rows={3}
			/>
		{/if}
	</FormSection>

	{#if isCreateMode}
		<FormSection
			title="Arquivos"
			description="Anexe arquivos PDF (máx. 10 MB cada) a este caso"
			columns="1"
		>
			<div class="space-y-4">
				<input
					bind:this={fileInput}
					type="file"
					accept="application/pdf,.pdf"
					multiple
					class="hidden"
					onchange={handleFilesSelected}
				/>
				<Button type="button" variant="outline" onclick={() => fileInput?.click()}>
					<UploadIcon class="mr-2 h-4 w-4" />
					Adicionar Arquivos
				</Button>

				{#if selectedFiles.length > 0}
					<div class="space-y-2">
						{#each selectedFiles as file, index (file.name + file.size)}
							<div class="flex items-center justify-between rounded-lg bg-muted/50 p-3">
								<div class="flex items-center gap-2">
									<FileTextIcon class="h-5 w-5" />
									<span class="text-sm">{file.name}</span>
									<span class="text-xs text-muted-foreground">
										({(file.size / (1024 * 1024)).toFixed(2)} MB)
									</span>
								</div>
								<Button
									variant="ghost"
									size="sm"
									class="h-6 w-6 p-0"
									type="button"
									onclick={() => removeFile(index)}
								>
									<X class="h-4 w-4" />
								</Button>
							</div>
						{/each}
					</div>
				{:else}
					<p class="text-sm text-muted-foreground">Nenhum arquivo selecionado</p>
				{/if}
			</div>
		</FormSection>
	{/if}

	<div class="flex items-center justify-between border-t border-border pt-6">
		<Button type="button" variant="outline" href="/casos">Cancelar</Button>
		<div class="flex gap-3">
			<Form.Button class="min-w-[140px]">
				{isCreateMode ? 'Criar Caso' : 'Salvar Alterações'}
			</Form.Button>
		</div>
	</div>
</form>
