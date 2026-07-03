<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import AdicionarFilaDialog from '$lib/components/adicionar-fila-dialog.svelte';
	import Plus from '@lucide/svelte/icons/plus';
	import PhoneCall from '@lucide/svelte/icons/phone-call';
	import Check from '@lucide/svelte/icons/check';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import { api } from '$lib/api-client';
	import { invalidateAll } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const fila = $derived(data.fila ?? []);

	let dialogOpen = $state(false);
	let busy = $state(false);

	const emAtendimento = $derived(fila.filter((f) => f.status === 1));
	const aguardando = $derived(fila.filter((f) => f.status === 0));

	async function chamarProximo() {
		if (busy) return;
		busy = true;
		try {
			await api.post('fila_atendimento/chamar-proximo');
			toast.success('Próximo atendimento iniciado');
			await invalidateAll();
		} catch (err: any) {
			toast.error(err?.message ?? 'Erro ao chamar próximo');
		} finally {
			busy = false;
		}
	}

	async function concluir(id: number) {
		if (busy) return;
		busy = true;
		try {
			await api.patch(`fila_atendimento/${id}/concluir`);
			toast.success('Atendimento concluído');
			await invalidateAll();
		} catch {
			toast.error('Erro ao concluir atendimento');
		} finally {
			busy = false;
		}
	}

	async function remover(id: number) {
		if (busy) return;
		busy = true;
		try {
			await api.delete(`fila_atendimento/${id}`);
			toast.success('Removido da fila');
			await invalidateAll();
		} catch {
			toast.error('Erro ao remover da fila');
		} finally {
			busy = false;
		}
	}
</script>

<div class="space-y-6">
	<div class="flex flex-wrap items-center justify-between gap-4">
		<div class="min-w-0">
			<h1 class="text-3xl font-bold tracking-tight">Fila de Atendimento</h1>
			<p class="text-muted-foreground">Gerencie a fila de pessoas aguardando atendimento</p>
		</div>
		<div class="flex shrink-0 gap-2">
			<Button variant="outline" onclick={() => (dialogOpen = true)}>
				<Plus class="mr-1 h-4 w-4" /> Adicionar à Fila
			</Button>
			<Button onclick={chamarProximo} disabled={busy || aguardando.length === 0}>
				<PhoneCall class="mr-1 h-4 w-4" /> Chamar Próximo
			</Button>
		</div>
	</div>

	<div class="rounded-lg border bg-card p-6">
		<h2 class="mb-4 text-xl font-semibold">Fila Atual</h2>

		{#if fila.length === 0}
			<div class="py-12 text-center text-muted-foreground">
				Nenhuma pessoa na fila. Clique em "Adicionar à Fila" para começar.
			</div>
		{:else}
			<div class="space-y-3">
				{#each [...emAtendimento, ...aguardando] as item (item.id)}
					<div
						class={[
							'rounded-lg border p-4',
							item.status === 1 && 'border-green-200 bg-green-50 dark:bg-green-950/30'
						]}
					>
						<div class="flex items-center justify-between gap-4">
							<div class="min-w-0">
								<div class="flex items-center gap-2">
									<h3 class="font-medium">#{item.senha} - {item.atendido_nome}</h3>
									{#if item.prioridade === 1}
										<Badge variant="destructive">Prioritário</Badge>
									{/if}
								</div>
								{#if item.atendido_cpf}
									<p class="text-sm text-muted-foreground">CPF: {item.atendido_cpf}</p>
								{/if}
								{#if item.tipo}
									<p class="text-sm text-muted-foreground">Tipo: {item.tipo}</p>
								{/if}
							</div>
							<div class="flex items-center gap-4">
								<div class="text-right">
									<p class="text-sm font-medium">{item.status_label}</p>
									{#if item.status === 0 && item.posicao != null}
										<p class="text-xs text-muted-foreground">Posição: {item.posicao}</p>
									{/if}
								</div>
								<div class="flex gap-1">
									{#if item.status === 1}
										<Button
											variant="ghost"
											size="sm"
											class="h-8 w-8 p-0"
											title="Concluir atendimento"
											disabled={busy}
											onclick={() => concluir(item.id)}
										>
											<Check class="h-4 w-4 text-green-600" />
										</Button>
									{/if}
									<Button
										variant="ghost"
										size="sm"
										class="h-8 w-8 p-0 text-destructive hover:text-destructive"
										title="Remover da fila"
										disabled={busy}
										onclick={() => remover(item.id)}
									>
										<Trash2 class="h-4 w-4" />
									</Button>
								</div>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<AdicionarFilaDialog bind:open={dialogOpen} onSuccess={() => invalidateAll()} />
