<script lang="ts">
	import AtendidoForm from '$lib/forms/atendido-form.svelte';
	import AssistidoForm from '$lib/forms/assistido-form.svelte';
	import { toast } from 'svelte-sonner';
	import Button from '$lib/components/ui/button/button.svelte';
	import { Badge } from '$lib/components/ui/badge';

	let { data }: { data: any } = $props();

	function onError(error: any) {
		toast.error(`Erro ao atualizar ${data.isAssistido ? 'assistido' : 'atendido'}`);
	}
</script>

<div class="min-h-screen bg-background">
	<div class="max-w-5xl py-1">
		<div class="mb-8">
			<div class="flex items-center justify-between">
				<div>
					<div class="flex items-center gap-3">
						<h1 class="text-3xl font-bold tracking-tight text-foreground">
							Editar {data.isAssistido ? 'Assistido' : 'Atendido'}
						</h1>
						{#if data.isAssistido}
							<Badge variant="default" class="bg-green-600">Assistido</Badge>
						{/if}
					</div>
					<p class="mt-2 text-muted-foreground">
						Atualize as informações de {data.atendido.nome}
					</p>
				</div>
				<Button variant="outline" href="/plantao/atendidos-assistidos">Voltar</Button>
			</div>
		</div>

		<div class="space-y-8">
			<AtendidoForm
				data={data.atendidoForm}
				atendidoId={data.atendido.id}
				isCreateMode={false}
				{onError}
			/>

			{#if data.isAssistido && data.assistidoForm}
				<div class="border-t pt-6">
					<h2 class="mb-6 text-2xl font-bold">Informações de Assistido</h2>
					<AssistidoForm
						data={data.assistidoForm}
						atendidoId={data.atendido.id}
						{onError}
						isAssistido={true}
					/>
				</div>
			{/if}
		</div>
	</div>
</div>
