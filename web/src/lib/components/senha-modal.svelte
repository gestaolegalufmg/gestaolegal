<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import { Label } from '$lib/components/ui/label';
	import { api } from '$lib/api-client';
	import { ApiException, type FilaItem, type SenhaPreview } from '$lib/types';
	import { PRIORIDADE_OPTIONS } from '$lib/constants/fila-atendimento';
	import { toast } from 'svelte-sonner';

	let {
		open = $bindable(false),
		atendidoId,
		atendidoNome,
		onIncluded
	}: {
		open?: boolean;
		atendidoId: number;
		atendidoNome?: string;
		onIncluded?: (item: FilaItem) => void;
	} = $props();

	let prioridade = $state<number | null>(null);
	let psicologia = $state(false);
	let senhaPreview = $state('');
	let previewLoading = $state(false);
	let submitting = $state(false);

	// Reinicia o estado sempre que o modal é aberto.
	$effect(() => {
		if (open) {
			prioridade = null;
			psicologia = false;
			senhaPreview = '';
		}
	});

	// Busca a prévia da senha quando um tipo é escolhido.
	$effect(() => {
		if (prioridade === null) return;

		const p = prioridade;
		previewLoading = true;
		api
			.get<SenhaPreview>(`fila_atendimento/preview?prioridade=${p}`)
			.then((res) => {
				senhaPreview = res.senha;
			})
			.catch((err) => {
				senhaPreview = '';
				if (err instanceof ApiException) toast.error(err.message);
			})
			.finally(() => {
				previewLoading = false;
			});
	});

	async function incluir() {
		if (prioridade === null) return;

		submitting = true;
		try {
			const item = await api.post<FilaItem>('fila_atendimento', {
				id_atendido: atendidoId,
				prioridade,
				psicologia
			});
			toast.success(`Atendido incluído na fila com a senha ${item.senha}`);
			open = false;
			onIncluded?.(item);
		} catch (err) {
			if (err instanceof ApiException) toast.error(err.message);
			else toast.error('Erro ao incluir na fila');
		} finally {
			submitting = false;
		}
	}
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="sm:max-w-2xl">
		<Dialog.Header>
			<Dialog.Title class="text-center text-xl">Escolha o tipo de senha</Dialog.Title>
			{#if atendidoNome}
				<Dialog.Description class="text-center">{atendidoNome}</Dialog.Description>
			{/if}
		</Dialog.Header>

		<div class="grid gap-6 py-2 sm:grid-cols-2 sm:divide-x sm:divide-border">
			<div class="space-y-4 sm:pr-6">
				{#each PRIORIDADE_OPTIONS as option (option.value)}
					<label class="flex cursor-pointer gap-3">
						<input
							type="radio"
							name="tipo-senha"
							value={option.value}
							checked={prioridade === option.value}
							onchange={() => (prioridade = option.value)}
							class="mt-1 h-4 w-4 shrink-0 accent-primary"
						/>
						<div class="space-y-0.5">
							<p class="leading-none font-semibold">{option.label}</p>
							<p class="text-sm text-muted-foreground">{option.descricao}</p>
						</div>
					</label>
				{/each}
			</div>

			<div class="flex flex-col items-center justify-center sm:pl-6">
				{#if prioridade !== null}
					<p class="text-muted-foreground">Senha do atendido</p>
					<p class="text-5xl font-bold text-primary">
						{previewLoading ? '···' : senhaPreview}
					</p>
				{:else}
					<p class="max-w-[220px] text-center text-sm text-muted-foreground">
						Selecione o tipo de senha para visualizar a prévia.
					</p>
				{/if}
			</div>
		</div>

		<div class="flex items-center justify-center gap-2">
			<Checkbox id="psicologia" bind:checked={psicologia} />
			<Label for="psicologia" class="cursor-pointer">Há atendimento da psicologia</Label>
		</div>

		<Dialog.Footer class="sm:justify-center">
			<Button variant="outline" onclick={() => (open = false)}>Voltar</Button>
			<Button onclick={incluir} disabled={prioridade === null || submitting}>
				Cadastrar e Incluir na Fila
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
