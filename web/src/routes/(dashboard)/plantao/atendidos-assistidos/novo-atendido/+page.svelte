<script lang="ts">
	import AtendidoForm from '$lib/forms/atendido-form.svelte';
	import type { PageData } from './$types';
	import { toast } from 'svelte-sonner';
	import Button from '$lib/components/ui/button/button.svelte';

	let { data }: { data: PageData } = $props();

	function onError(error: any) {
		toast.error('Erro ao criar atendido');
	}
</script>

<div class="min-h-screen bg-background">
	<div class="max-w-5xl py-1">
		<div class="mb-8">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold tracking-tight text-foreground">Novo Atendido</h1>
					<p class="mt-2 text-muted-foreground">Cadastre um novo atendido no sistema</p>
				</div>
				<Button variant="outline" href="/plantao/atendidos-assistidos">Voltar</Button>
			</div>
		</div>
		<AtendidoForm data={data.form} isCreateMode={true} {onError} />
	</div>
</div>
