<script lang="ts">
	import { afterNavigate } from '$app/navigation';
	import { onMount } from 'svelte';
	import Bell from '@lucide/svelte/icons/bell';
	import { api } from '$lib/api-client';
	import { Button } from '$lib/components/ui/button';
	import { naoLidas } from '$lib/stores/notificacoes';

	const INTERVALO_MS = 60_000;

	async function atualizar() {
		try {
			const data = await api.get<{ total: number }>('notificacao/nao-lidas');
			naoLidas.set(data.total);
		} catch {
			/* sem rede ou sessão expirada: mantém o valor anterior */
		}
	}

	onMount(() => {
		atualizar();
		const timer = setInterval(atualizar, INTERVALO_MS);
		return () => clearInterval(timer);
	});

	afterNavigate(() => {
		atualizar();
	});
</script>

<Button
	variant="ghost"
	size="icon"
	href="/notificacoes"
	class="relative"
	title={$naoLidas > 0 ? `${$naoLidas} notificação(ões) não lida(s)` : 'Notificações'}
	aria-label="Notificações"
>
	<Bell class="h-5 w-5" />
	{#if $naoLidas > 0}
		<span
			class="absolute -top-0.5 -right-0.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-destructive px-1 text-[11px] font-semibold text-white"
		>
			{$naoLidas > 99 ? '99+' : $naoLidas}
		</span>
	{/if}
</Button>
