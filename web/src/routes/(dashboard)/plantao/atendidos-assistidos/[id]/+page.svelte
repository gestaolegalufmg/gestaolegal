<script lang="ts">
	import type { PageData } from './$types';
	import Button from '$lib/components/ui/button/button.svelte';
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import Edit from '@lucide/svelte/icons/edit';
	import UserPlus from '@lucide/svelte/icons/user-plus';
	import ListPlus from '@lucide/svelte/icons/list-plus';
	import Eye from '@lucide/svelte/icons/eye';
	import Scale from '@lucide/svelte/icons/scale';
	import Briefcase from '@lucide/svelte/icons/briefcase';
	import SenhaModal from '$lib/components/senha-modal.svelte';
	import { formatDateOnly } from '$lib/utils/date';

	let { data }: { data: PageData } = $props();
	let { atendido } = data;
	const casos = $derived(data.casos ?? []);
	const orientacoes = $derived(data.orientacoes ?? []);

	function capitalize(value: string | null | undefined): string {
		if (!value) return '--';
		return value.charAt(0).toUpperCase() + value.slice(1);
	}

	let senhaModalOpen = $state(false);

	function formatDate(dateString: string | null): string {
		if (!dateString) return 'Não informado';
		const date = new Date(dateString);
		// Birth dates are calendar dates — format in UTC to avoid a timezone day-shift.
		return date.toLocaleDateString('pt-BR', { timeZone: 'UTC' });
	}

	function formatCurrency(value: number | null): string {
		if (value === null || value === undefined) return 'R$ 0,00';
		return new Intl.NumberFormat('pt-BR', {
			style: 'currency',
			currency: 'BRL'
		}).format(value);
	}

	const comoConheceuLabels: Record<string, string> = {
		assist: 'Assistidos/ex-assistidos',
		integ: 'Integrantes/ex-integrantes da UFMG',
		orgaos_pub: 'Órgãos públicos',
		meios_com: 'Meios de comunicação',
		nucleos: 'Núcleos de prática jurídica',
		conhec: 'Amigos, familiares ou conhecidos',
		outros: 'Outros'
	};

	const estadoCivilLabels: Record<string, string> = {
		solteiro: 'Solteiro',
		casado: 'Casado',
		divorciado: 'Divorciado',
		separado: 'Separado',
		uniao: 'União estável',
		viuvo: 'Viúvo'
	};

	const sexoLabels: Record<string, string> = {
		M: 'Masculino',
		F: 'Feminino',
		O: 'Outro'
	};

	const racaLabels: Record<string, string> = {
		indigena: 'Indígena',
		preta: 'Preta',
		parda: 'Parda',
		amarela: 'Amarela',
		branca: 'Branca',
		nao_declarado: 'Prefere não declarar'
	};

	const escolaridadeLabels: Record<string, string> = {
		nao_frequentou: 'Não frequentou a escola',
		infantil_inc: 'Educação infantil incompleta',
		infantil_comp: 'Educação infantil completa',
		fundamental1_inc: 'Fundamental 1° ao 5° ano incompleto',
		fundamental1_comp: 'Fundamental 1° ao 5° ano completo',
		fundamental2_inc: 'Fundamental 6° ao 9° ano incompleto',
		fundamental2_comp: 'Fundamental 6° ao 9° ano completo',
		medio_inc: 'Ensino médio incompleto',
		medio_comp: 'Ensino médio completo',
		tecnico_inc: 'Curso técnico incompleto',
		tecnico_comp: 'Curso técnico completo',
		superior_inc: 'Ensino superior incompleto',
		superior_comp: 'Ensino superior completo',
		nao_info: 'Não informou'
	};

	const beneficioLabels: Record<string, string> = {
		ben_prestacao_continuada: 'Benefício de prestação continuada',
		renda_basica: 'Renda Básica',
		bolsa_escola: 'Bolsa escola',
		bolsa_moradia: 'Bolsa moradia',
		cesta_basica: 'Cesta básica',
		valegas: 'Vale Gás',
		nao: 'Não',
		outro: 'Outro',
		nao_info: 'Não informou'
	};

	const moradiaLabels: Record<string, string> = {
		propria_quitada: 'Própria quitada',
		propria_financiada: 'Própria financiada',
		moradia_cedida: 'Cedida',
		ocupada_irregular: 'Ocupada/Irregular',
		em_construcao: 'Em construção',
		alugada: 'Alugada',
		parentes_amigos: 'Casa de parentes ou amigos',
		situacao_rua: 'Situação de rua'
	};

	const participacaoRendaLabels: Record<string, string> = {
		principal: 'Principal responsável',
		contribuinte: 'Contribuinte',
		dependente: 'Dependente'
	};
</script>

<div class="min-h-screen bg-background">
	<div class="max-w-5xl py-1">
		<div class="mb-8">
			<div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
				<div class="min-w-0">
					<div class="flex flex-wrap items-center gap-2">
						<h1 class="text-3xl font-bold tracking-tight break-words text-foreground">
							{atendido.nome}
						</h1>
						<Badge variant={atendido.status === 1 ? 'default' : 'secondary'}>
							{atendido.status === 1 ? 'Ativo' : 'Inativo'}
						</Badge>
						{#if atendido.assistido}
							<Badge variant="default" class="bg-green-600">Assistido</Badge>
						{:else}
							<Badge variant="secondary">Atendido</Badge>
						{/if}
					</div>
					<p class="mt-2 text-muted-foreground">
						Informações detalhadas do {atendido.assistido ? 'assistido' : 'atendido'}
					</p>
				</div>
				<div class="flex flex-wrap gap-2 lg:justify-end">
					<Button variant="outline" href="/plantao/atendidos-assistidos">Voltar</Button>
					<Button variant="default" onclick={() => (senhaModalOpen = true)}>
						<ListPlus class="mr-2 h-4 w-4" />
						Incluir na Fila de Atendimento
					</Button>
					<Button variant="default" href="/plantao/atendidos-assistidos/{atendido.id}/editar">
						<Edit class="mr-2 h-4 w-4" />
						Editar
					</Button>
					{#if !atendido.assistido}
						<Button
							variant="default"
							class="bg-green-600 hover:bg-green-700"
							href="/plantao/atendidos-assistidos/{atendido.id}/tornar-assistido"
						>
							<UserPlus class="mr-2 h-4 w-4" />
							Tornar Assistido
						</Button>
					{/if}
				</div>
			</div>
		</div>

		<div class="space-y-6">
			<Card.Root>
				<Card.Header>
					<Card.Title>Dados Pessoais</Card.Title>
				</Card.Header>
				<Card.Content class="grid gap-4 md:grid-cols-2">
					<div>
						<p class="text-sm text-muted-foreground">CPF</p>
						<p class="font-medium">{atendido.cpf}</p>
					</div>

					<div>
						<p class="text-sm text-muted-foreground">Data de Nascimento</p>
						<p class="font-medium">{formatDate(atendido.data_nascimento)}</p>
					</div>

					{#if atendido.cnpj}
						<div>
							<p class="text-sm text-muted-foreground">CNPJ</p>
							<p class="font-medium">{atendido.cnpj}</p>
						</div>
					{/if}

					<div>
						<p class="text-sm text-muted-foreground">Estado Civil</p>
						<p class="font-medium">
							{estadoCivilLabels[atendido.estado_civil] || atendido.estado_civil}
						</p>
					</div>

					<div>
						<p class="text-sm text-muted-foreground">Email</p>
						<p class="font-medium">{atendido.email}</p>
					</div>

					<div>
						<p class="text-sm text-muted-foreground">Celular</p>
						<p class="font-medium">{atendido.celular}</p>
					</div>

					{#if atendido.telefone}
						<div>
							<p class="text-sm text-muted-foreground">Telefone</p>
							<p class="font-medium">{atendido.telefone}</p>
						</div>
					{/if}
				</Card.Content>
			</Card.Root>

			{#if atendido.endereco}
				<Card.Root>
					<Card.Header>
						<Card.Title>Endereço</Card.Title>
					</Card.Header>
					<Card.Content class="grid gap-4 md:grid-cols-2">
						<div class="md:col-span-2">
							<p class="text-sm text-muted-foreground">Logradouro</p>
							<p class="font-medium">
								{atendido.endereco.logradouro}, {atendido.endereco.numero}
								{#if atendido.endereco.complemento}
									- {atendido.endereco.complemento}
								{/if}
							</p>
						</div>

						<div>
							<p class="text-sm text-muted-foreground">Bairro</p>
							<p class="font-medium">{atendido.endereco.bairro}</p>
						</div>

						<div>
							<p class="text-sm text-muted-foreground">CEP</p>
							<p class="font-medium">{atendido.endereco.cep}</p>
						</div>

						<div>
							<p class="text-sm text-muted-foreground">Cidade</p>
							<p class="font-medium">{atendido.endereco.cidade}</p>
						</div>

						<div>
							<p class="text-sm text-muted-foreground">Estado</p>
							<p class="font-medium">{atendido.endereco.estado}</p>
						</div>
					</Card.Content>
				</Card.Root>
			{/if}

			<Card.Root>
				<Card.Header>
					<Card.Title>Como Conheceu o DAJ</Card.Title>
				</Card.Header>
				<Card.Content class="grid gap-4 md:grid-cols-2">
					<div>
						<p class="text-sm text-muted-foreground">Como conheceu</p>
						<p class="font-medium">
							{comoConheceuLabels[atendido.como_conheceu] || atendido.como_conheceu}
						</p>
					</div>

					{#if atendido.indicacao_orgao}
						<div>
							<p class="text-sm text-muted-foreground">Indicação do Órgão</p>
							<p class="font-medium">{atendido.indicacao_orgao}</p>
						</div>
					{/if}

					<div>
						<p class="text-sm text-muted-foreground">Procurou outro local?</p>
						<p class="font-medium">{atendido.procurou_outro_local === 'sim' ? 'Sim' : 'Não'}</p>
					</div>

					{#if atendido.procurou_qual_local}
						<div>
							<p class="text-sm text-muted-foreground">Qual local procurou?</p>
							<p class="font-medium">{atendido.procurou_qual_local}</p>
						</div>
					{/if}
				</Card.Content>
			</Card.Root>

			{#if atendido.pj_constituida === 'sim'}
				<Card.Root>
					<Card.Header>
						<Card.Title>Informações de Pessoa Jurídica</Card.Title>
					</Card.Header>
					<Card.Content class="grid gap-4 md:grid-cols-2">
						<div>
							<p class="text-sm text-muted-foreground">PJ Constituída</p>
							<p class="font-medium">Sim</p>
						</div>

						<div>
							<p class="text-sm text-muted-foreground">É o representante legal?</p>
							<p class="font-medium">{atendido.repres_legal ? 'Sim' : 'Não'}</p>
						</div>

						{#if !atendido.repres_legal && atendido.nome_repres_legal}
							<div class="md:col-span-2">
								<p class="text-sm text-muted-foreground">Nome do Representante Legal</p>
								<p class="font-medium">{atendido.nome_repres_legal}</p>
							</div>

							{#if atendido.cpf_repres_legal}
								<div>
									<p class="text-sm text-muted-foreground">CPF do Representante</p>
									<p class="font-medium">{atendido.cpf_repres_legal}</p>
								</div>
							{/if}

							{#if atendido.rg_repres_legal}
								<div>
									<p class="text-sm text-muted-foreground">RG do Representante</p>
									<p class="font-medium">{atendido.rg_repres_legal}</p>
								</div>
							{/if}

							{#if atendido.contato_repres_legal}
								<div>
									<p class="text-sm text-muted-foreground">Contato do Representante</p>
									<p class="font-medium">{atendido.contato_repres_legal}</p>
								</div>
							{/if}

							{#if atendido.nascimento_repres_legal}
								<div>
									<p class="text-sm text-muted-foreground">Data de Nascimento do Representante</p>
									<p class="font-medium">{formatDate(atendido.nascimento_repres_legal)}</p>
								</div>
							{/if}
						{/if}
					</Card.Content>
				</Card.Root>
			{/if}

			{#if atendido.obs}
				<Card.Root>
					<Card.Header>
						<Card.Title>Observações sobre o Atendido</Card.Title>
					</Card.Header>
					<Card.Content>
						<p class="text-sm whitespace-pre-wrap">{atendido.obs}</p>
					</Card.Content>
				</Card.Root>
			{/if}

			<div class="grid gap-6 md:grid-cols-2">
				<Card.Root>
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<Briefcase class="h-5 w-5" /> Casos
						</Card.Title>
					</Card.Header>
					<Card.Content>
						{#if casos.length === 0}
							<p class="py-4 text-center text-sm text-muted-foreground">
								Nenhum caso vinculado a esta pessoa.
							</p>
						{:else}
							<div class="space-y-2">
								{#each casos as caso (caso.id)}
									<div class="flex items-center justify-between rounded-lg bg-muted/50 p-3">
										<div class="min-w-0">
											<p class="truncate font-medium">
												Caso #{caso.id} — {capitalize(caso.area_direito)}
											</p>
											<p class="text-xs text-muted-foreground">
												{capitalize(caso.situacao_deferimento)}
												{#if caso.data_criacao}· {formatDateOnly(caso.data_criacao)}{/if}
											</p>
										</div>
										<Button variant="ghost" size="sm" href="/casos/{caso.id}">
											<Eye class="h-4 w-4" />
										</Button>
									</div>
								{/each}
							</div>
						{/if}
					</Card.Content>
				</Card.Root>

				<Card.Root>
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<Scale class="h-5 w-5" /> Orientações Jurídicas
						</Card.Title>
					</Card.Header>
					<Card.Content>
						{#if orientacoes.length === 0}
							<p class="py-4 text-center text-sm text-muted-foreground">
								Nenhuma orientação jurídica vinculada a esta pessoa.
							</p>
						{:else}
							<div class="space-y-2">
								{#each orientacoes as orientacao (orientacao.id)}
									<div class="flex items-center justify-between rounded-lg bg-muted/50 p-3">
										<div class="min-w-0">
											<p class="truncate font-medium">{capitalize(orientacao.area_direito)}</p>
											<p class="text-xs text-muted-foreground">
												{#if orientacao.sub_area}{capitalize(orientacao.sub_area)} ·
												{/if}
												{#if orientacao.data_criacao}{formatDateOnly(orientacao.data_criacao)}{/if}
											</p>
										</div>
										<Button
											variant="ghost"
											size="sm"
											href="/plantao/orientacoes-juridicas/{orientacao.id}"
										>
											<Eye class="h-4 w-4" />
										</Button>
									</div>
								{/each}
							</div>
						{/if}
					</Card.Content>
				</Card.Root>
			</div>

			{#if atendido.assistido}
				<div class="border-t pt-6">
					<h2 class="mb-6 text-2xl font-bold">Informações de Assistido</h2>

					<div class="space-y-6">
						<Card.Root>
							<Card.Header>
								<Card.Title>Dados Pessoais Complementares</Card.Title>
							</Card.Header>
							<Card.Content class="grid gap-4 md:grid-cols-2">
								<div>
									<p class="text-sm text-muted-foreground">Sexo</p>
									<p class="font-medium">
										{sexoLabels[atendido.assistido.sexo] || atendido.assistido.sexo}
									</p>
								</div>

								<div>
									<p class="text-sm text-muted-foreground">RG</p>
									<p class="font-medium">{atendido.assistido.rg}</p>
								</div>

								<div>
									<p class="text-sm text-muted-foreground">Profissão</p>
									<p class="font-medium">{atendido.assistido.profissao}</p>
								</div>

								<div>
									<p class="text-sm text-muted-foreground">Raça/Cor</p>
									<p class="font-medium">
										{racaLabels[atendido.assistido.raca] || atendido.assistido.raca}
									</p>
								</div>

								<div class="md:col-span-2">
									<p class="text-sm text-muted-foreground">Grau de Instrução</p>
									<p class="font-medium">
										{escolaridadeLabels[atendido.assistido.grau_instrucao] ||
											atendido.assistido.grau_instrucao}
									</p>
								</div>
							</Card.Content>
						</Card.Root>

						<Card.Root>
							<Card.Header>
								<Card.Title>Informações Financeiras</Card.Title>
							</Card.Header>
							<Card.Content class="grid gap-4 md:grid-cols-2">
								<div>
									<p class="text-sm text-muted-foreground">Salário</p>
									<p class="font-medium">{formatCurrency(atendido.assistido.salario)}</p>
								</div>

								<div>
									<p class="text-sm text-muted-foreground">Renda Familiar</p>
									<p class="font-medium">{formatCurrency(atendido.assistido.renda_familiar)}</p>
								</div>

								<div>
									<p class="text-sm text-muted-foreground">Benefício</p>
									<p class="font-medium">
										{beneficioLabels[atendido.assistido.beneficio] || atendido.assistido.beneficio}
									</p>
								</div>

								{#if atendido.assistido.qual_beneficio}
									<div>
										<p class="text-sm text-muted-foreground">Qual benefício?</p>
										<p class="font-medium">{atendido.assistido.qual_beneficio}</p>
									</div>
								{/if}

								<div>
									<p class="text-sm text-muted-foreground">Contribui com INSS?</p>
									<p class="font-medium">
										{atendido.assistido.contribui_inss === 'sim'
											? 'Sim'
											: atendido.assistido.contribui_inss === 'enq_trabalhava'
												? 'Enquanto trabalhava'
												: atendido.assistido.contribui_inss === 'nao'
													? 'Não'
													: 'Não informou'}
									</p>
								</div>

								<div>
									<p class="text-sm text-muted-foreground">Participação na Renda</p>
									<p class="font-medium">
										{participacaoRendaLabels[atendido.assistido.participacao_renda] ||
											atendido.assistido.participacao_renda}
									</p>
								</div>

								<div>
									<p class="text-sm text-muted-foreground">Pessoas na Moradia</p>
									<p class="font-medium">{atendido.assistido.qtd_pessoas_moradia}</p>
								</div>
							</Card.Content>
						</Card.Root>

						<Card.Root>
							<Card.Header>
								<Card.Title>Moradia e Patrimônio</Card.Title>
							</Card.Header>
							<Card.Content class="grid gap-4 md:grid-cols-2">
								<div>
									<p class="text-sm text-muted-foreground">Tipo de Moradia</p>
									<p class="font-medium">
										{moradiaLabels[atendido.assistido.tipo_moradia] ||
											atendido.assistido.tipo_moradia}
									</p>
								</div>

								<div>
									<p class="text-sm text-muted-foreground">Possui outros imóveis?</p>
									<p class="font-medium">
										{atendido.assistido.possui_outros_imoveis
											? `Sim (${atendido.assistido.quantos_imoveis})`
											: 'Não'}
									</p>
								</div>

								<div>
									<p class="text-sm text-muted-foreground">Possui veículos?</p>
									<p class="font-medium">
										{atendido.assistido.possui_veiculos
											? `Sim (${atendido.assistido.quantos_veiculos})`
											: 'Não'}
									</p>
								</div>

								{#if atendido.assistido.possui_veiculos && atendido.assistido.ano_veiculo}
									<div>
										<p class="text-sm text-muted-foreground">Ano do(s) veículo(s)</p>
										<p class="font-medium">{atendido.assistido.ano_veiculo}</p>
									</div>

									{#if atendido.assistido.possui_veiculos_obs}
										<div class="md:col-span-2">
											<p class="text-sm text-muted-foreground">Observações sobre veículos</p>
											<p class="text-sm whitespace-pre-wrap">
												{atendido.assistido.possui_veiculos_obs}
											</p>
										</div>
									{/if}
								{/if}
							</Card.Content>
						</Card.Root>

						{#if atendido.assistido.doenca_grave_familia === 'sim'}
							<Card.Root>
								<Card.Header>
									<Card.Title>Saúde</Card.Title>
								</Card.Header>
								<Card.Content class="grid gap-4 md:grid-cols-2">
									<div>
										<p class="text-sm text-muted-foreground">Doença grave na família</p>
										<p class="font-medium">Sim</p>
									</div>

									{#if atendido.assistido.pessoa_doente}
										<div>
											<p class="text-sm text-muted-foreground">Quem é a pessoa doente?</p>
											<p class="font-medium">
												{atendido.assistido.pessoa_doente === 'propria_pessoa'
													? 'Própria pessoa'
													: atendido.assistido.pessoa_doente === 'companheira_companheiro'
														? 'Cônjuge ou Companheiro(a)'
														: atendido.assistido.pessoa_doente === 'filhos'
															? 'Filhos'
															: atendido.assistido.pessoa_doente === 'pais'
																? 'Pais'
																: atendido.assistido.pessoa_doente === 'avos'
																	? 'Avós'
																	: atendido.assistido.pessoa_doente === 'sogros'
																		? 'Sogros'
																		: 'Outros'}
											</p>
										</div>
									{/if}

									{#if atendido.assistido.gastos_medicacao !== null}
										<div>
											<p class="text-sm text-muted-foreground">Gastos com Medicação</p>
											<p class="font-medium">
												{formatCurrency(atendido.assistido.gastos_medicacao)}
											</p>
										</div>
									{/if}

									{#if atendido.assistido.pessoa_doente_obs}
										<div class="md:col-span-2">
											<p class="text-sm text-muted-foreground">Observações sobre a doença</p>
											<p class="text-sm whitespace-pre-wrap">
												{atendido.assistido.pessoa_doente_obs}
											</p>
										</div>
									{/if}
								</Card.Content>
							</Card.Root>
						{/if}

						{#if atendido.assistido.obs}
							<Card.Root>
								<Card.Header>
									<Card.Title>Observações sobre o Assistido</Card.Title>
								</Card.Header>
								<Card.Content>
									<p class="text-sm whitespace-pre-wrap">{atendido.assistido.obs}</p>
								</Card.Content>
							</Card.Root>
						{/if}
					</div>
				</div>
			{/if}
		</div>
	</div>
</div>

<SenhaModal bind:open={senhaModalOpen} atendidoId={atendido.id} atendidoNome={atendido.nome} />
