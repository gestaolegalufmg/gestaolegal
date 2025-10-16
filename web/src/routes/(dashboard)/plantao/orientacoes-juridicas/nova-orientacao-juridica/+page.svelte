<script lang="ts">
	import OrientacaoJuridicaForm from '$lib/forms/orientacao-juridica-form.svelte';
	import type { PageData } from './$types';
	import { toast } from 'svelte-sonner';
	import Button from '$lib/components/ui/button/button.svelte';

	let { data }: { data: PageData } = $props();

	function onError(error: any) {
		toast.error('Erro ao criar orientação jurídica');
	}
</script>

<div class="max-w-5xl py-1">
	<div class="mb-8">
		<div class="flex items-center justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight text-foreground">Nova Orientação Jurídica</h1>
				<p class="mt-2 text-muted-foreground">Cadastre uma nova orientação jurídica no sistema</p>
			</div>
			<Button variant="outline" href="/plantao/orientacoes-juridicas">Voltar</Button>
		</div>
	</div>
	<OrientacaoJuridicaForm data={data.form} isCreateMode={true} {onError} />
</div>
