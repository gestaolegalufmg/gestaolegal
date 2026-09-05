<script lang="ts">
	import { api } from '$lib/api-client';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Table from '$lib/components/ui/table';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { invalidateAll } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { mensagemDeErro } from '$lib/utils/erros';
	import { formatDateTime } from '$lib/utils/date';
	import type { Unidade } from '$lib/types';
	import type { PageProps } from './$types';
	import Edit from '@lucide/svelte/icons/edit';

	let { data }: PageProps = $props();
	const unidades = $derived(data.unidades);

	let open = $state(false);
	let emEdicao = $state<Unidade | null>(null);
	let nome = $state('');
	let sigla = $state('');
	let ativa = $state(true);
	let salvando = $state(false);

	function abrirNova() {
		emEdicao = null;
		nome = '';
		sigla = '';
		ativa = true;
		open = true;
	}

	function abrirEdicao(unidade: Unidade) {
		emEdicao = unidade;
		nome = unidade.nome;
		sigla = unidade.sigla;
		ativa = unidade.ativa;
		open = true;
	}

	async function salvar() {
		if (!nome.trim() || !sigla.trim()) {
			toast.error('Nome e sigla são obrigatórios');
			return;
		}

		salvando = true;
		try {
			const payload = { nome: nome.trim(), sigla: sigla.trim(), ativa };
			if (emEdicao) {
				await api.put(`unidades/${emEdicao.id}`, payload);
				toast.success('Unidade atualizada');
			} else {
				await api.post('unidades/', payload);
				toast.success('Unidade criada');
			}
			open = false;
			// Recarrega o layout do dashboard também: é ele que ressincroniza a
			// unidade ativa do seletor com a lista atual.
			await invalidateAll();
		} catch (err) {
			toast.error(mensagemDeErro(err, 'Erro ao salvar unidade'));
		} finally {
			salvando = false;
		}
	}
</script>

<svelte:head>
	<title>Unidades - Gestão Legal</title>
</svelte:head>

<div class="max-w-4xl space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold tracking-tight">Unidades</h1>
			<p class="mt-2 text-muted-foreground">
				Locais de atendimento da DAJ. Cada usuário enxerga apenas os dados da unidade ativa.
			</p>
		</div>
		<Button onclick={abrirNova}>Nova Unidade</Button>
	</div>

	<div class="rounded-lg border bg-card">
		<Table.Root>
			<Table.Header>
				<Table.Row>
					<Table.Head>Nome</Table.Head>
					<Table.Head class="w-[100px]">Sigla</Table.Head>
					<Table.Head class="w-[110px]">Situação</Table.Head>
					<Table.Head class="w-[170px]">Criada em</Table.Head>
					<Table.Head class="w-[80px] text-right">Ações</Table.Head>
				</Table.Row>
			</Table.Header>
			<Table.Body>
				{#each unidades as unidade (unidade.id)}
					<Table.Row>
						<Table.Cell class="font-medium">{unidade.nome}</Table.Cell>
						<Table.Cell class="font-mono">{unidade.sigla}</Table.Cell>
						<Table.Cell>
							<Badge variant={unidade.ativa ? 'default' : 'secondary'}>
								{unidade.ativa ? 'Ativa' : 'Inativa'}
							</Badge>
						</Table.Cell>
						<Table.Cell>{formatDateTime(unidade.criado)}</Table.Cell>
						<Table.Cell class="text-right">
							<Button
								variant="ghost"
								size="icon"
								title="Editar"
								onclick={() => abrirEdicao(unidade)}
							>
								<Edit class="h-4 w-4" />
							</Button>
						</Table.Cell>
					</Table.Row>
				{:else}
					<Table.Row>
						<Table.Cell colspan={5} class="py-8 text-center text-muted-foreground">
							Nenhuma unidade cadastrada.
						</Table.Cell>
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</div>
</div>

<Dialog.Root bind:open>
	<Dialog.Content class="sm:max-w-md">
		<Dialog.Header>
			<Dialog.Title>{emEdicao ? 'Editar unidade' : 'Nova unidade'}</Dialog.Title>
			<Dialog.Description>
				O nome e a sigla são únicos. A sigla aparece no seletor do cabeçalho.
			</Dialog.Description>
		</Dialog.Header>

		<div class="space-y-4">
			<div class="space-y-1">
				<Label for="unidade-nome">Nome</Label>
				<Input id="unidade-nome" bind:value={nome} placeholder="Belo Horizonte" />
			</div>
			<div class="space-y-1">
				<Label for="unidade-sigla">Sigla</Label>
				<Input id="unidade-sigla" bind:value={sigla} placeholder="BH" />
			</div>
			<label class="flex cursor-pointer items-center gap-2">
				<Checkbox bind:checked={ativa} />
				<span class="text-sm">Unidade ativa</span>
			</label>
			{#if emEdicao && !ativa}
				<p class="text-sm text-muted-foreground">
					Unidades inativas somem desta lista e do seletor de unidade.
				</p>
			{/if}
		</div>

		<Dialog.Footer>
			<Button variant="outline" onclick={() => (open = false)} disabled={salvando}>Cancelar</Button>
			<Button onclick={salvar} disabled={salvando}>
				{salvando ? 'Salvando...' : 'Salvar'}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
