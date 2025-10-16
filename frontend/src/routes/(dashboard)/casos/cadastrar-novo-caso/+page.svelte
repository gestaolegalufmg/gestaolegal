<script lang="ts">
	import CasoForm from '$lib/forms/caso-form.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	function handleError(error: any) {
		console.error('Error creating caso:', error);
	}
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Novo Caso</h1>
		<p class="text-muted-foreground">Cadastre um novo caso no sistema</p>
	</div>

	<div class="bg-card rounded-lg border p-6">
		<CasoForm
			data={data.form}
			onError={handleError}
			isCreateMode={true}
			usuarios={data.usuarios}
			assistidos={data.assistidos}
		/>
	</div>
</div>
