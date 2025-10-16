<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import InfoCard from '$lib/components/ui/info-card.svelte';
	import PencilIcon from '@lucide/svelte/icons/pencil';
	import KeyIcon from '@lucide/svelte/icons/key';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const { user, me, canView = true } = data;
	const isAdmin = $derived(me.urole === 'admin');

	const personalData = [
		{ label: 'Data de Nascimento', value: new Date(user.nascimento).toLocaleDateString('pt-BR') },
		{ label: 'Sexo', value: user.sexo },
		{ label: 'CPF', value: user.cpf },
		{ label: 'RG', value: user.rg },
		{ label: 'Profissão', value: user.profissao },
		{ label: 'OAB', value: user.oab },
		{ label: 'Email', value: user.email }
	];

	const addressData = [
		{ label: 'Logradouro', value: user.endereco.logradouro },
		{ label: 'Número', value: user.endereco.numero },
		{ label: 'Complemento', value: user.endereco.complemento },
		{ label: 'Bairro', value: user.endereco.bairro },
		{ label: 'CEP', value: user.endereco.cep },
		{ label: 'Cidade', value: user.endereco.cidade },
		{ label: 'Estado', value: user.endereco.estado }
	];

	const registrationData = [
		{ label: 'Email', value: user.email },
		{ label: 'Telefone', value: user.telefone },
		{ label: 'Data de Inclusão', value: new Date(user.data_entrada).toLocaleDateString('pt-BR') },
		{
			label: 'Data de Exclusão',
			value: user.data_saida,
			formatter: (value: string) => new Date(value).toLocaleDateString('pt-BR')
		}
	];

	const academicData = [{ label: 'Possui bolsa', value: user.bolsista }];

	const agendaAtendimento = [
		{ label: 'Dia da semana e horário do atendimento', value: user.horario_atendimento }
	];
</script>

<div class="space-y-6">
	{#if canView}
		<div class="flex justify-between items-center">
			<h1 class="text-3xl font-bold tracking-tight">{user.nome}</h1>
			<div class="flex gap-2">
				{#if user.id === me.id || isAdmin}
					<Button href={`/usuarios/${user.id}/alterar-senha`} variant="outline">
						<KeyIcon />
						Alterar Senha
					</Button>
				{/if}
				{#if isAdmin}
					<Button href={`/usuarios/${user.id}/editar`}>
						<PencilIcon />
						Editar
					</Button>
				{/if}
			</div>
		</div>

		<div class="grid gap-6 md:grid-cols-2">
			<InfoCard title="Dados Pessoais" items={personalData} />
			<InfoCard title="Endereço" items={addressData} />
			<InfoCard title="Dados Cadastrais" items={registrationData} />
			<InfoCard title="Dados Acadêmicos" items={academicData} />
			<InfoCard title="Agenda de Atendimento" items={agendaAtendimento} />
		</div>
	{:else}
		<p class="text-muted-foreground">Você não tem permissão para visualizar usuários.</p>
	{/if}
</div>
