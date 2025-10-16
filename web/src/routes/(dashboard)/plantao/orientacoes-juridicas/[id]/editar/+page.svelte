<script lang="ts">
	import OrientacaoJuridicaForm from '$lib/forms/orientacao-juridica-form.svelte';
	import type { PageData } from './$types';
	import { toast } from 'svelte-sonner';
	import Button from '$lib/components/ui/button/button.svelte';

	let { data }: { data: PageData } = $props();

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
						Editar Orientação Jurídica
					</h1>
					<p class="mt-2 text-muted-foreground">
						Atualize as informações da orientação jurídica no sistema
					</p>
				</div>
				<Button variant="outline" href="/plantao/orientacoes-juridicas">Voltar</Button>
			</div>
		</div>
	</div>
	<OrientacaoJuridicaForm
		data={data.form}
		orientacao={data.orientacao}
		orientacaoId={data.orientacao.id}
		{onError}
	/>
</div>
