<script lang="ts">
	import { invalidate } from '$app/navigation';
	import { page } from '$app/state';
	import { toast } from 'svelte-sonner';
	import Download from '@lucide/svelte/icons/download';
	import Edit from '@lucide/svelte/icons/edit';
	import Eye from '@lucide/svelte/icons/eye';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import { usePaginatedFilters } from '$lib';
	import { api } from '$lib/api-client';
	import DataTable from '$lib/components/data-table.svelte';
	import { Button } from '$lib/components/ui/button';
	import Input from '$lib/components/ui/input/input.svelte';
	import { ARQUIVO_PAPEIS_EDITAM, ARQUIVO_PAPEIS_EXCLUEM, type ListArquivo } from '$lib/types';
	import { baixarArquivoDaApi } from '$lib/utils/download';
	import { mensagemDeErro } from '$lib/utils/erros';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const { arquivos, me } = $derived(data);

	const podeEditar = $derived(ARQUIVO_PAPEIS_EDITAM.includes(me.urole));
	const podeExcluir = $derived(ARQUIVO_PAPEIS_EXCLUEM.includes(me.urole));

	const { filters, applyFilters, setFilters } = usePaginatedFilters<{ search: string }>({
		initialFilters: { search: page.url.searchParams.get('search') ?? '' },
		buildParams: (f) => ({ search: f.search })
	});

	async function baixar(a: ListArquivo) {
		try {
			await baixarArquivoDaApi(`arquivo/${a.id}/download`, a.nome);
		} catch (err) {
			toast.error(mensagemDeErro(err, 'Erro ao baixar arquivo'));
		}
	}

	async function excluir(a: ListArquivo) {
		try {
			await api.delete(`arquivo/${a.id}`);
			toast.success('Arquivo excluído');
			await invalidate('app:arquivos');
		} catch (err) {
			toast.error(mensagemDeErro(err, 'Erro ao excluir arquivo'));
		}
	}
</script>

<div class="space-y-6">
	<div class="flex flex-wrap items-center justify-between gap-4">
		<div>
			<h1 class="text-3xl font-bold tracking-tight">Arquivos</h1>
			<p class="mt-2 text-muted-foreground">Documentos e modelos compartilhados da organização.</p>
		</div>
		{#if podeEditar}
			<Button variant="default" class="shrink-0 whitespace-nowrap" href="/arquivos/cadastrar-arquivo">
				Cadastrar Arquivo
			</Button>
		{/if}
	</div>

	<div class="min-w-0 rounded-lg border bg-card p-6">
		<div class="mb-4 flex items-center gap-2">
			<Input
				bind:value={filters.search}
				ondebounceinput={() => {
					setFilters({ search: filters.search });
					applyFilters();
				}}
				debounceMs={500}
				placeholder="Buscar por título ou descrição..."
				class="max-w-sm"
			/>
		</div>

		<DataTable
			data={arquivos}
			onPageChange={(p) => applyFilters({ page: p })}
			columns={[
				{ header: 'Título', key: 'titulo', class: 'w-[220px]' },
				{ header: 'Descrição', key: 'descricao', type: 'preview', previewClass: 'max-w-[320px]' },
				{ header: 'Arquivo', key: 'nome', class: 'w-[200px]', type: 'preview', previewClass: 'max-w-[200px]' },
				{ header: 'Cadastrado por', key: 'criado_por', class: 'w-[160px]' },
				{ header: 'Data', key: 'data_criacao', type: 'date', class: 'w-[110px]' }
			]}
			actions={{
				class: 'w-[160px] text-right',
				buttons: [
					{ title: 'Baixar', icon: Download, onClick: (a: ListArquivo) => baixar(a) },
					{ title: 'Visualizar', icon: Eye, href: (a: ListArquivo) => `/arquivos/${a.id}` },
					{
						title: 'Editar',
						icon: Edit,
						show: () => podeEditar,
						href: (a: ListArquivo) => `/arquivos/${a.id}/editar`
					},
					{
						title: 'Excluir',
						icon: Trash2,
						show: () => podeExcluir,
						onClick: (a: ListArquivo) => excluir(a),
						confirm: {
							title: 'Excluir arquivo?',
							description: 'O registro e o arquivo serão apagados definitivamente.',
							confirmText: 'Excluir'
						},
						class: 'h-8 w-8 p-0 text-destructive hover:text-destructive'
					}
				]
			}}
		/>
	</div>
</div>
