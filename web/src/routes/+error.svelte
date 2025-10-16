<script lang="ts">
	import { page } from '$app/stores';
	import Button from '$lib/components/ui/button/button.svelte';
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { AlertTriangle, Home, RefreshCw } from '@lucide/svelte';

	let { error }: { error: App.Error } = $props();

	const errorMessage = $derived(error?.message || 'Ocorreu um erro inesperado');
	const status = $derived($page.status);
</script>

<div class="flex min-h-screen items-center justify-center bg-background p-4">
	<Card class="w-full max-w-md">
		<CardHeader class="text-center">
			<div
				class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10"
			>
				<AlertTriangle class="h-6 w-6 text-destructive" />
			</div>
			<CardTitle class="text-xl">
				{#if status === 404}
					Página não encontrada
				{:else if status === 401}
					Não autorizado
				{:else if status === 403}
					Acesso negado
				{:else if status >= 500}
					Erro do servidor
				{:else}
					Erro
				{/if}
			</CardTitle>
		</CardHeader>
		<CardContent class="space-y-4 text-center">
			<p class="text-muted-foreground">{errorMessage}</p>

			<div class="flex flex-col gap-2">
				{#if status === 401}
					<Button onclick={() => (window.location.href = '/login')} class="w-full">
						Fazer Login
					</Button>
				{:else if status !== 404}
					<Button onclick={() => window.location.reload()} variant="outline" class="w-full">
						<RefreshCw class="mr-2 h-4 w-4" />
						Tentar Novamente
					</Button>
				{/if}

				<Button onclick={() => (window.location.href = '/')} variant="ghost" class="w-full">
					<Home class="mr-2 h-4 w-4" />
					Página Inicial
				</Button>
			</div>
		</CardContent>
	</Card>
</div>
