<script lang="ts">
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import Download from '@lucide/svelte/icons/download';
	import Edit from '@lucide/svelte/icons/edit';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import { api } from '$lib/api-client';
	import ConfirmAction from '$lib/components/confirm-action.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import * as Card from '$lib/components/ui/card';
	import { ARQUIVO_PAPEIS_EDITAM, ARQUIVO_PAPEIS_EXCLUEM } from '$lib/types';
	import { formatDateTime } from '$lib/utils/date';
	import { baixarArquivoDaApi } from '$lib/utils/download';
	import { mensagemDeErro } from '$lib/utils/erros';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	const { arquivo, me } = $derived(data);

	const podeEditar = $derived(ARQUIVO_PAPEIS_EDITAM.includes(me.urole));
	const podeExcluir = $derived(ARQUIVO_PAPEIS_EXCLUEM.includes(me.urole));

	async function baixar() {
		try {
			await baixarArquivoDaApi(`arquivo/${arquivo.id}/download`, arquivo.nome);
		} catch (err) {
			toast.error(mensagemDeErro(err, 'Erro ao baixar arquivo'));
		}
	}

	async function excluir() {
		try {
			await api.delete(`arquivo/${arquivo.id}`);
			toast.success('Arquivo excluído');
			await goto('/arquivos');
		} catch (err) {
			toast.error(mensagemDeErro(err, 'Erro ao excluir arquivo'));
		}
	}
</script>

<div class="max-w-4xl py-1">
	<div class="mb-8 flex flex-wrap items-start justify-between gap-4">
		<div class="min-w-0">
			<h1 class="text-3xl font-bold tracking-tight text-foreground">{arquivo.titulo}</h1>
			<p class="mt-2 text-muted-foreground">
				Cadastrado em {arquivo.data_criacao
					? formatDateTime(arquivo.data_criacao)
					: 'data não informada'}
			</p>
		</div>
		<div class="flex flex-wrap gap-2">
			<Button variant="outline" href="/arquivos">Voltar</Button>
			<Button onclick={baixar}><Download class="mr-2 h-4 w-4" /> Baixar</Button>
			{#if podeEditar}
				<Button variant="outline" href={`/arquivos/${arquivo.id}/editar`}>
					<Edit class="mr-2 h-4 w-4" /> Editar
				</Button>
			{/if}
			{#if podeExcluir}
				<ConfirmAction
					title="Excluir arquivo?"
					description="O registro e o arquivo serão apagados definitivamente."
					confirmText="Excluir"
					buttonVariant="destructive"
					buttonSize="default"
					onConfirm={excluir}
				>
					{#snippet trigger()}
						<Trash2 class="mr-2 h-4 w-4" /> Excluir
					{/snippet}
				</ConfirmAction>
			{/if}
		</div>
	</div>

	<Card.Root>
		<Card.Header>
			<Card.Title>Detalhes</Card.Title>
		</Card.Header>
		<Card.Content class="space-y-4">
			<div>
				<p class="text-sm font-medium text-muted-foreground">Arquivo</p>
				<p class="break-all">{arquivo.nome}</p>
			</div>
			<div>
				<p class="text-sm font-medium text-muted-foreground">Descrição</p>
				<p class="whitespace-pre-wrap">{arquivo.descricao || 'Sem descrição'}</p>
			</div>
		</Card.Content>
	</Card.Root>
</div>
