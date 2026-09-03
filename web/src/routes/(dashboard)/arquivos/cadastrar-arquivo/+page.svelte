<script lang="ts">
	import ArquivoForm from '$lib/forms/arquivo-form.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
</script>

<div class="max-w-3xl py-1">
	<div class="mb-8 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold tracking-tight text-foreground">Cadastrar Arquivo</h1>
			<p class="mt-2 text-muted-foreground">Compartilhe um documento com toda a organização.</p>
		</div>
		<Button variant="outline" href="/arquivos">Voltar</Button>
	</div>
	<ArquivoForm />
</div>
