<script lang="ts">
	import ProcessoForm from '$lib/forms/processo-form.svelte';
	import type { PageData } from './$types';
	import { toast } from 'svelte-sonner';
	import Button from '$lib/components/ui/button/button.svelte';

	let { data }: { data: PageData } = $props();
	const { processo } = data;

	function onUpdate(data: any) {
		toast.success('Processo atualizado com sucesso');
	}

	function onError(error: App.Error | Error | string) {
		if (typeof error === 'string') {
			toast.error(error);
			return;
		}
		toast.error(error.message as string);
	}
</script>

<div class="min-h-screen bg-background">
	<div class="max-w-4xl py-1">
		<div class="mb-8">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold tracking-tight text-foreground">
						Editar Processo {processo.identificacao || `#${processo.id}`}
					</h1>
					<p class="mt-2 text-muted-foreground">Atualize as informações do processo no sistema</p>
				</div>
				<Button variant="outline" href="/casos/{processo.id_caso}/processos/{processo.id}"
					>Voltar</Button
				>
			</div>
		</div>
	</div>
	<ProcessoForm data={data.form} {onUpdate} {onError} isCreateMode={false} />
</div>
