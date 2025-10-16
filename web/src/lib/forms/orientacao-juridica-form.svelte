<script lang="ts">
	import * as Form from '$lib/components/ui/form';
	import { superForm, type Infer, type SuperValidated } from 'sveltekit-superforms';
	import { zod4Client } from 'sveltekit-superforms/adapters';
	import {
		orientacaoJuridicaCreateFormSchema,
		type OrientacaoJuridicaCreateFormSchema
	} from './schemas/orientacao-juridica-schema';
	import { SimpleSelect, SimpleTextArea } from '$lib/components/forms';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import AtendidoSelectorDialog from '$lib/components/atendido-selector-dialog.svelte';
	import { Badge } from '$lib/components/ui/badge';
	import type { Atendido } from '$lib/types';
	import X from '@lucide/svelte/icons/x';
	import UserPlus from '@lucide/svelte/icons/user-plus';
	import {
		AREA_DIREITO_OPTIONS,
		SUB_AREA_DIREITO_ADMINISTRATIVO_OPTIONS,
		SUB_AREA_DIREITO_CIVEL_OPTIONS
	} from '$lib/constants';
	import { toast } from 'svelte-sonner';
	import { api } from '$lib/api-client';
	import { goto } from '$app/navigation';
	import { get } from 'svelte/store';

	let {
		data,
		isCreateMode = false,
		orientacaoId,
		onError,
		onUpdate,
		hideSubmitButton = false,
		orientacao
	}: {
		data: SuperValidated<Infer<OrientacaoJuridicaCreateFormSchema>>;
		isCreateMode?: boolean;
		orientacaoId?: number;
		onError?: (error: any) => void;
		onUpdate?: (responseData: any) => void;
		hideSubmitButton?: boolean;
		orientacao?: any;
	} = $props();

	const form = superForm(data, {
		SPA: true,
		dataType: 'json',
		validators: zod4Client(orientacaoJuridicaCreateFormSchema),
		resetForm: false,
		onSubmit: async () => {
			const rawData = get(formData);
			const currentData =
				typeof structuredClone === 'function'
					? structuredClone(rawData)
					: JSON.parse(JSON.stringify(rawData));
			const targetOrientacaoId = orientacaoId ?? orientacao?.id;

			try {
				const response = isCreateMode
					? await api.post('orientacao_juridica', currentData)
					: await api.put(`orientacao_juridica/${targetOrientacaoId}`, currentData);

				if (!response.ok) {
					const errorData = await response.json().catch(() => ({}));
					toast.error(errorData.message || 'Erro ao salvar orientação jurídica');
					onError?.(errorData);
					return;
				}

				const responseData = await response.json();
				toast.success(
					isCreateMode
						? 'Orientação jurídica criada com sucesso!'
						: 'Orientação jurídica atualizada com sucesso!'
				);
				onUpdate?.(responseData);

				const redirectTo = isCreateMode
					? '/plantao/orientacoes-juridicas'
					: `/plantao/orientacoes-juridicas/${responseData.id}`;

				goto(redirectTo);
			} catch (error) {
				console.error('Orientacao juridica form error:', error);
				toast.error('Erro ao salvar orientação jurídica. Por favor, tente novamente.');
				onError?.(error);
			}
		}
	});

	const { form: formData, enhance } = form;

	let selectedAtendidos = $state<Atendido[]>(orientacao?.atendidos || []);

	let showSubArea = $derived(
		$formData.area_direito === 'civel' || $formData.area_direito === 'administrativo'
	);
	let subAreaOptions = $derived(
		$formData.area_direito === 'civel'
			? SUB_AREA_DIREITO_CIVEL_OPTIONS
			: $formData.area_direito === 'administrativo'
				? SUB_AREA_DIREITO_ADMINISTRATIVO_OPTIONS
				: []
	);

	function handleAtendidosSelected(atendidos: Atendido[]) {
		selectedAtendidos = atendidos;
		$formData.atendidos_ids = atendidos.map((a) => a.id);
	}

	function removeAtendido(atendidoId: number) {
		selectedAtendidos = selectedAtendidos.filter((a) => a.id !== atendidoId);
		$formData.atendidos_ids = selectedAtendidos.map((a) => a.id);
	}
</script>

<form method="POST" use:enhance class="space-y-6">
	<Card.Root>
		<Card.Header>
			<Card.Title>Informações da Orientação Jurídica</Card.Title>
			<Card.Description>Preencha os dados sobre a orientação jurídica prestada</Card.Description>
		</Card.Header>
		<Card.Content class="grid gap-4">
			<SimpleSelect
				label="Área do Direito"
				name="area_direito"
				{form}
				bind:value={$formData.area_direito}
				options={AREA_DIREITO_OPTIONS}
				placeholder="Selecione a área do direito"
			/>

			{#if showSubArea}
				<SimpleSelect
					label="Sub-área"
					name="sub_area"
					{form}
					bind:value={$formData.sub_area}
					options={subAreaOptions}
					placeholder="Selecione a sub-área"
				/>
			{/if}

			<SimpleTextArea
				label="Descrição"
				name="descricao"
				{form}
				bind:value={$formData.descricao}
				placeholder="Descreva detalhadamente a orientação jurídica prestada..."
				rows={6}
			/>
		</Card.Content>
	</Card.Root>

	<Card.Root>
		<Card.Header>
			<Card.Title>Atendidos Associados</Card.Title>
			<Card.Description>
				Selecione os atendidos relacionados a esta orientação jurídica
			</Card.Description>
		</Card.Header>
		<Card.Content class="space-y-4">
			<AtendidoSelectorDialog
				{form}
				name="atendidos_ids"
				bind:selectedAtendidosIds={$formData.atendidos_ids}
				onSelect={handleAtendidosSelected}
			>
				{#snippet trigger()}
					<UserPlus class="mr-2 h-4 w-4" />
					Adicionar Atendidos
				{/snippet}
			</AtendidoSelectorDialog>

			{#if selectedAtendidos.length > 0}
				<div class="space-y-2">
					<p class="text-sm font-medium">
						{selectedAtendidos.length} atendido(s) selecionado(s):
					</p>
					<div class="flex flex-wrap gap-2">
						{#each selectedAtendidos as atendido (atendido.id)}
							<Badge variant="secondary" class="py-1 pr-1 pl-3">
								<span class="mr-2">{atendido.nome}</span>
								<Button
									variant="ghost"
									size="sm"
									class="h-4 w-4 p-0 hover:bg-transparent"
									onclick={() => removeAtendido(atendido.id)}
									type="button"
								>
									<X class="h-3 w-3" />
								</Button>
							</Badge>
						{/each}
					</div>
				</div>
			{:else}
				<p class="text-sm text-muted-foreground">Nenhum atendido selecionado</p>
			{/if}
		</Card.Content>
	</Card.Root>

	{#if !hideSubmitButton}
		<div class="flex justify-end gap-4">
			<Button type="button" variant="outline" href="/plantao/orientacoes-juridicas">
				Cancelar
			</Button>
			<Button type="submit">
				{isCreateMode ? 'Criar Orientação Jurídica' : 'Salvar Alterações'}
			</Button>
		</div>
	{/if}
</form>
