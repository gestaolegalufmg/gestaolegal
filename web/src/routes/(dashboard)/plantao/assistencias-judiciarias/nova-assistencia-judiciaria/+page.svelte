<script lang="ts">
	import AssistenciaJudiciariaForm from '$lib/forms/assistencia-judiciaria-form.svelte';
	import type { PageData } from './$types';
	import { toast } from 'svelte-sonner';
	import Button from '$lib/components/ui/button/button.svelte';

	let { data }: { data: PageData } = $props();

	function onError() {
		toast.error('Erro ao criar assistência judiciária');
	}
</script>

<div class="max-w-5xl py-1">
	<div class="mb-8">
		<div class="flex items-center justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight text-foreground">
					Nova Assistência Judiciária
				</h1>
				<p class="mt-2 text-muted-foreground">
					Cadastre um novo órgão de assistência judiciária no sistema
				</p>
			</div>
			<Button variant="outline" href="/plantao/assistencias-judiciarias">Voltar</Button>
		</div>
	</div>
	<AssistenciaJudiciariaForm data={data.form} isCreateMode={true} {onError} />
</div>
