<script lang="ts">
	import { goto, invalidate } from '$app/navigation';
	import { page } from '$app/state';
	import { toast } from 'svelte-sonner';
	import Bell from '@lucide/svelte/icons/bell';
	import CheckCheck from '@lucide/svelte/icons/check-check';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import { api } from '$lib/api-client';
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import { naoLidas } from '$lib/stores/notificacoes';
	import { destinoDaNotificacao, type Notificacao } from '$lib/types';
	import { formatDateTime } from '$lib/utils/date';
	import { mensagemDeErro } from '$lib/utils/erros';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const { notificacoes } = $derived(data);

	const totalPaginas = $derived(Math.max(1, Math.ceil(notificacoes.total / notificacoes.per_page)));

	const tipoLabel: Record<string, string> = {
		caso: 'Caso',
		evento: 'Evento',
		lembrete: 'Lembrete',
		plantao: 'Plantão'
	};

	async function atualizarContador() {
		try {
			const d = await api.get<{ total: number }>('notificacao/nao-lidas');
			naoLidas.set(d.total);
		} catch {
			/* ignora */
		}
	}

	async function marcarLida(n: Notificacao) {
		if (n.lida) return;
		try {
			await api.patch(`notificacao/${n.id}/lida`);
			n.lida = true;
			await atualizarContador();
		} catch (err) {
			toast.error(mensagemDeErro(err, 'Erro ao marcar como lida'));
		}
	}

	async function abrir(n: Notificacao) {
		await marcarLida(n);
		const destino = destinoDaNotificacao(n);
		if (destino) await goto(destino);
	}

	async function marcarTodas() {
		try {
			await api.patch('notificacao/lidas');
			toast.success('Todas as notificações foram marcadas como lidas');
			await invalidate('app:notificacoes');
			await atualizarContador();
		} catch (err) {
			toast.error(mensagemDeErro(err, 'Erro ao marcar notificações'));
		}
	}

	function irParaPagina(p: number) {
		const params = new URLSearchParams(page.url.searchParams);
		params.set('page', String(p));
		goto(`/notificacoes?${params.toString()}`);
	}
</script>

<div class="max-w-4xl space-y-6">
	<div class="flex flex-wrap items-center justify-between gap-4">
		<div>
			<h1 class="text-3xl font-bold tracking-tight">Notificações</h1>
			<p class="mt-2 text-muted-foreground">
				Avisos de casos, eventos, lembretes e abertura do plantão em que você foi incluído.
			</p>
		</div>
		{#if notificacoes.items.some((n) => !n.lida)}
			<Button variant="outline" onclick={marcarTodas}>
				<CheckCheck class="mr-2 h-4 w-4" /> Marcar todas como lidas
			</Button>
		{/if}
	</div>

	{#if notificacoes.items.length === 0}
		<div class="flex flex-col items-center gap-2 rounded-lg border bg-card p-10 text-center">
			<Bell class="h-8 w-8 text-muted-foreground" />
			<p class="text-muted-foreground">Você não tem notificações.</p>
		</div>
	{:else}
		<ul class="divide-y rounded-lg border bg-card">
			{#each notificacoes.items as n (n.id)}
				{@const destino = destinoDaNotificacao(n)}
				<li class="flex flex-wrap items-center gap-3 p-4 {n.lida ? '' : 'bg-primary/5'}">
					<span
						class="h-2.5 w-2.5 shrink-0 rounded-full {n.lida ? 'bg-transparent' : 'bg-primary'}"
						title={n.lida ? 'Lida' : 'Não lida'}
					></span>
					<div class="min-w-0 flex-1">
						<p class={n.lida ? '' : 'font-semibold'}>{n.acao}</p>
						<p class="text-sm text-muted-foreground">
							{n.executor ?? 'Sistema'} · {formatDateTime(n.data_criacao ?? n.data)}
							{#if n.id_usu_notificar === null}
								· aviso geral
							{/if}
						</p>
					</div>
					{#if n.tipo}
						<Badge variant="outline">{tipoLabel[n.tipo] ?? n.tipo}</Badge>
					{/if}
					{#if destino}
						<Button variant="ghost" size="sm" onclick={() => abrir(n)}>
							<ExternalLink class="mr-1 h-4 w-4" /> Abrir
						</Button>
					{:else if !n.lida}
						<Button variant="ghost" size="sm" onclick={() => marcarLida(n)}>Marcar como lida</Button
						>
					{/if}
				</li>
			{/each}
		</ul>

		{#if totalPaginas > 1}
			<div class="flex items-center justify-between text-sm text-muted-foreground">
				<span>Página {notificacoes.page} de {totalPaginas} · {notificacoes.total} notificações</span
				>
				<div class="flex gap-2">
					<Button
						variant="outline"
						size="sm"
						disabled={notificacoes.page <= 1}
						onclick={() => irParaPagina(notificacoes.page - 1)}>Anterior</Button
					>
					<Button
						variant="outline"
						size="sm"
						disabled={notificacoes.page >= totalPaginas}
						onclick={() => irParaPagina(notificacoes.page + 1)}>Próxima</Button
					>
				</div>
			</div>
		{/if}
	{/if}
</div>
