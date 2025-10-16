<script lang="ts">
	import CasoForm from '$lib/forms/caso-form.svelte';
	import type { PageData } from './$types';
	import { toast } from 'svelte-sonner';
	import Button from '$lib/components/ui/button/button.svelte';

	let { data }: { data: PageData } = $props();

	function onUpdate(data: any) {
		toast.success('Caso atualizado com sucesso');
	}

	function onError(error: App.Error | Error | string) {
		if (typeof error === 'string') {
			toast.error(error);
			return;
		}
		toast.error(error.message as string);
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold tracking-tight">Editar Caso #{data.caso.id}</h1>
			<p class="text-muted-foreground">Atualize as informações do caso no sistema</p>
		</div>
		<Button variant="outline" href="/casos/{data.caso.id}">Voltar</Button>
	</div>

	<div class="bg-card rounded-lg border p-6">
		<CasoForm
			data={data.form}
			{onUpdate}
			{onError}
			isCreateMode={false}
			usuarios={data.usuarios}
			assistidos={data.assistidos}
		/>
	</div>
</div>
