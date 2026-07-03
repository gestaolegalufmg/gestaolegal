<script lang="ts">
	import type { PageData } from './$types';
	import Button from '$lib/components/ui/button/button.svelte';
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import Edit from '@lucide/svelte/icons/edit';

	let { data }: { data: PageData } = $props();
	let { assistencia } = $derived(data);

	const areaLabels: Record<string, string> = {
		administrativo: 'Administrativo',
		ambiental: 'Ambiental',
		civel: 'Cível',
		empresarial: 'Empresarial',
		penal: 'Penal',
		trabalhista: 'Trabalhista'
	};

	const regiaoLabels: Record<string, string> = {
		norte: 'Norte',
		sul: 'Sul',
		leste: 'Leste',
		oeste: 'Oeste',
		noroeste: 'Noroeste',
		centro_sul: 'Centro-Sul',
		nordeste: 'Nordeste',
		pampulha: 'Pampulha',
		barreiro: 'Barreiro',
		venda_nova: 'Venda Nova',
		contagem: 'Contagem',
		betim: 'Betim'
	};

	function enderecoLinha(): string {
		const e = assistencia.endereco;
		if (!e) return 'Não informado';
		const parts = [
			`${e.logradouro}, ${e.numero}`,
			e.complemento,
			e.bairro,
			`${e.cidade} - ${e.estado}`,
			e.cep
		].filter(Boolean);
		return parts.join(' · ');
	}
</script>

<div class="min-h-screen bg-background">
	<div class="max-w-5xl py-1">
		<div class="mb-8">
			<div class="flex items-center justify-between">
				<div>
					<div class="flex items-center gap-3">
						<h1 class="text-3xl font-bold tracking-tight text-foreground">{assistencia.nome}</h1>
						<Badge variant={assistencia.status ? 'default' : 'secondary'}>
							{assistencia.status ? 'Ativo' : 'Inativo'}
						</Badge>
						<Badge variant="outline">
							{regiaoLabels[assistencia.regiao] || assistencia.regiao}
						</Badge>
					</div>
					<p class="mt-2 text-muted-foreground">Detalhes da assistência judiciária</p>
				</div>
				<div class="flex gap-2">
					<Button variant="outline" href="/plantao/assistencias-judiciarias">Voltar</Button>
					<Button variant="default" href="/plantao/assistencias-judiciarias/{assistencia.id}/editar">
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
						<p class="text-sm text-muted-foreground">Região</p>
						<p class="font-medium">{regiaoLabels[assistencia.regiao] || assistencia.regiao}</p>
					</div>
					<div>
						<p class="text-sm text-muted-foreground">Telefone</p>
						<p class="font-medium">{assistencia.telefone}</p>
					</div>
					<div>
						<p class="text-sm text-muted-foreground">E-mail</p>
						<p class="font-medium">{assistencia.email}</p>
					</div>
					<div>
						<p class="text-sm text-muted-foreground">Endereço</p>
						<p class="font-medium">{enderecoLinha()}</p>
					</div>
					<div class="md:col-span-2">
						<p class="text-sm text-muted-foreground">Áreas Atendidas</p>
						<div class="mt-1 flex flex-wrap gap-2">
							{#each assistencia.areas_atendidas as area}
								<Badge variant="secondary">{areaLabels[area] || area}</Badge>
							{/each}
						</div>
					</div>
				</Card.Content>
			</Card.Root>

			<Card.Root>
				<Card.Header>
					<Card.Title>Orientações Encaminhadas</Card.Title>
					<Card.Description>
						Orientações jurídicas associadas a esta assistência judiciária
					</Card.Description>
				</Card.Header>
				<Card.Content>
					{#if assistencia.orientacoes && assistencia.orientacoes.length > 0}
						<div class="space-y-2">
							{#each assistencia.orientacoes as orientacao}
								<div class="flex items-center justify-between rounded-md bg-muted p-3">
									<div>
										<p class="font-medium">
											{areaLabels[orientacao.area_direito] || orientacao.area_direito}
										</p>
										<p class="line-clamp-1 text-sm text-muted-foreground">{orientacao.descricao}</p>
									</div>
									<Button
										variant="outline"
										size="sm"
										href="/plantao/orientacoes-juridicas/{orientacao.id}"
									>
										Ver Orientação
									</Button>
								</div>
							{/each}
						</div>
					{:else}
						<p class="text-sm text-muted-foreground">Nenhuma orientação encaminhada</p>
					{/if}
				</Card.Content>
			</Card.Root>
		</div>
	</div>
</div>
