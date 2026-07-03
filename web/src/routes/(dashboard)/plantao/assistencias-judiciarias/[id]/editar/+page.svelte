<script lang="ts">
	import AssistenciaJudiciariaForm from '$lib/forms/assistencia-judiciaria-form.svelte';
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
						Editar Assistência Judiciária
					</h1>
					<p class="mt-2 text-muted-foreground">
						Atualize as informações da assistência judiciária no sistema
					</p>
				</div>
				<Button variant="outline" href="/plantao/assistencias-judiciarias">Voltar</Button>
			</div>
		</div>
	</div>
	<AssistenciaJudiciariaForm
		data={data.form}
		assistenciaId={data.assistencia.id}
		{onError}
	/>
</div>
