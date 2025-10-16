<script lang="ts">
	import AssistidoForm from '$lib/forms/assistido-form.svelte';
	import type { PageData } from './$types';
	import { toast } from 'svelte-sonner';
	import Button from '$lib/components/ui/button/button.svelte';
	import * as Card from '$lib/components/ui/card';

	let { data }: { data: PageData } = $props();

	function onError(error: any) {
		toast.error('Erro ao tornar assistido');
	}
</script>

<div class="min-h-screen bg-background">
	<div class="max-w-5xl py-1">
		<div class="mb-8">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold tracking-tight text-foreground">Tornar Assistido</h1>
					<p class="mt-2 text-muted-foreground">
						Complete as informações para tornar {data.atendido.nome} um assistido
					</p>
				</div>
				<Button variant="outline" href="/plantao/atendidos-assistidos">Voltar</Button>
			</div>
		</div>

		<Card.Root class="mb-6">
			<Card.Header>
				<Card.Title>Dados do Atendido</Card.Title>
			</Card.Header>
			<Card.Content class="grid gap-2">
				<div class="grid grid-cols-2 gap-4">
					<div>
						<p class="text-sm text-muted-foreground">Nome</p>
						<p class="font-medium">{data.atendido.nome}</p>
					</div>
					<div>
						<p class="text-sm text-muted-foreground">CPF</p>
						<p class="font-medium">{data.atendido.cpf}</p>
					</div>
					<div>
						<p class="text-sm text-muted-foreground">Email</p>
						<p class="font-medium">{data.atendido.email}</p>
					</div>
					<div>
						<p class="text-sm text-muted-foreground">Celular</p>
						<p class="font-medium">{data.atendido.celular}</p>
					</div>
				</div>
			</Card.Content>
		</Card.Root>

		<AssistidoForm data={data.form} {onError} />
	</div>
</div>
