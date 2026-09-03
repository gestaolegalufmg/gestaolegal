<script lang="ts">
	import ArquivoForm from '$lib/forms/arquivo-form.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
</script>

<div class="max-w-3xl py-1">
	<div class="mb-8 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold tracking-tight text-foreground">Editar Arquivo</h1>
			<p class="mt-2 text-muted-foreground">Altere o título, a descrição ou substitua o arquivo.</p>
		</div>
		<Button variant="outline" href={`/arquivos/${data.arquivo.id}`}>Voltar</Button>
	</div>
	{#key data.arquivo.id}
		<ArquivoForm arquivo={data.arquivo} />
	{/key}
</div>
