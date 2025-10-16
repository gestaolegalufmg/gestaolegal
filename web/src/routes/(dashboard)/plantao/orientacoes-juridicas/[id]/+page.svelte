<script lang="ts">
	import type { PageData } from './$types';
	import Button from '$lib/components/ui/button/button.svelte';
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import Edit from '@lucide/svelte/icons/edit';

	let { data }: { data: PageData } = $props();
	let { orientacao } = data;

	function formatDate(dateString: string | null | undefined): string {
		if (!dateString) return 'Não informado';
		const date = new Date(dateString);
		return date.toLocaleDateString('pt-BR', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	const areaDireitoLabels: Record<string, string> = {
		administrativo: 'Administrativo',
		ambiental: 'Ambiental',
		civel: 'Cível',
		empresarial: 'Empresarial',
		penal: 'Penal',
		trabalhista: 'Trabalhista'
	};

	const subAreaLabels: Record<string, string> = {
		administrativo: 'Administrativo',
		previdenciario: 'Previdenciário',
		tributario: 'Tributário',
		consumidor: 'Consumidor',
		contratos: 'Contratos',
		resp_civil: 'Responsabilidade Civil',
		responsabilidade_civil: 'Responsabilidade Civil',
		reais: 'Reais',
		familia: 'Família',
		sucessoes: 'Sucessões'
	};
</script>

<div class="min-h-screen bg-background">
	<div class="max-w-5xl py-1">
		<div class="mb-8">
			<div class="flex items-center justify-between">
				<div>
					<div class="flex items-center gap-3">
						<h1 class="text-3xl font-bold tracking-tight text-foreground">Orientação Jurídica</h1>
						<Badge variant={orientacao.status ? 'default' : 'secondary'}>
							{orientacao.status ? 'Ativo' : 'Inativo'}
						</Badge>
						<Badge variant="outline">
							{areaDireitoLabels[orientacao.area_direito] || orientacao.area_direito}
						</Badge>
					</div>
					<p class="mt-2 text-muted-foreground">Detalhes da orientação jurídica</p>
				</div>
				<div class="flex gap-2">
					<Button variant="outline" href="/plantao/orientacoes-juridicas">Voltar</Button>
					<Button variant="default" href="/plantao/orientacoes-juridicas/{orientacao.id}/editar">
						<Edit class="mr-2 h-4 w-4" />
						Editar
					</Button>
				</div>
			</div>
		</div>

		<div class="space-y-6">
			<Card.Root>
				<Card.Header>
					<Card.Title>Informações Gerais</Card.Title>
				</Card.Header>
				<Card.Content class="grid gap-4 md:grid-cols-2">
					<div>
						<p class="text-sm text-muted-foreground">Área do Direito</p>
						<p class="font-medium">
							{areaDireitoLabels[orientacao.area_direito] || orientacao.area_direito}
						</p>
					</div>

					{#if orientacao.sub_area}
						<div>
							<p class="text-sm text-muted-foreground">Sub-área</p>
							<p class="font-medium">
								{subAreaLabels[orientacao.sub_area] || orientacao.sub_area}
							</p>
						</div>
					{/if}

					<div>
						<p class="text-sm text-muted-foreground">Data de Criação</p>
						<p class="font-medium">{formatDate(orientacao.data_criacao)}</p>
					</div>

					<div>
						<p class="text-sm text-muted-foreground">Status</p>
						<p class="font-medium">
							{orientacao.status ? 'Ativo' : 'Inativo'}
						</p>
					</div>

					{#if orientacao.usuario}
						<div class="md:col-span-2">
							<p class="text-sm text-muted-foreground">Criado por</p>
							<p class="font-medium">{orientacao.usuario.nome}</p>
						</div>
					{/if}
				</Card.Content>
			</Card.Root>

			<Card.Root>
				<Card.Header>
					<Card.Title>Descrição</Card.Title>
				</Card.Header>
				<Card.Content>
					<p class="text-sm whitespace-pre-wrap">{orientacao.descricao}</p>
				</Card.Content>
			</Card.Root>

			{#if orientacao.atendidos && orientacao.atendidos.length > 0}
				<Card.Root>
					<Card.Header>
						<Card.Title>Partes Envolvidas</Card.Title>
					</Card.Header>
					<Card.Content>
						<div class="space-y-2">
							{#each orientacao.atendidos as atendido}
								<div class="flex items-center justify-between rounded-md bg-muted p-3">
									<p class="font-medium">{atendido.nome}</p>
									<Button
										variant="outline"
										size="sm"
										href="/plantao/atendidos-assistidos/{atendido.id}"
									>
										Ver Detalhes
									</Button>
								</div>
							{/each}
						</div>
					</Card.Content>
				</Card.Root>
			{/if}
		</div>
	</div>
</div>
