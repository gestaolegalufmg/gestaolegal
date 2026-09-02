<script lang="ts">
	import NavMain from './nav-main.svelte';
	import NavUser from './nav-user.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import type { ComponentProps } from 'svelte';
	import CompanyLogo from './company-logo.svelte';
	import type { User } from '$lib/types';
	import UsersIcon from '@lucide/svelte/icons/users';
	import ClockIcon from '@lucide/svelte/icons/clock';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import ChartBarIcon from '@lucide/svelte/icons/bar-chart-3';

	type NavItem = {
		title: string;
		url: string;
		// Quando presente, o item só aparece para os papéis listados. A
		// autorização de verdade é feita no backend; esconder o item é só UX.
		roles?: string[];
	};

	const baseNavMain: (NavItem & { icon: unknown; isActive?: boolean; items: NavItem[] })[] = [
		{
			title: 'Gestão de Usuários',
			url: '/usuarios',
			icon: UsersIcon,
			isActive: true,
			roles: ['admin'],
			items: []
		},
		{
			title: 'Plantão',
			url: '/plantao',
			icon: ClockIcon,
			items: [
				{
					title: 'Escala do Plantão',
					url: '/plantao/escala'
				},
				{
					title: 'Registro de Presença',
					url: '/plantao/registro-presenca'
				},
				{
					title: 'Confirmar Presença',
					url: '/plantao/confirmar-presenca',
					roles: ['admin', 'colab_proj', 'prof']
				},
				{
					title: 'Atendidos e Assistidos',
					url: '/plantao/atendidos-assistidos'
				},
				{
					title: 'Fila de atendimento',
					url: '/plantao/fila-atendimento'
				},
				{
					title: 'Orientações Jurídicas',
					url: '/plantao/orientacoes-juridicas'
				},
				{
					title: 'Assistências Judiciárias',
					url: '/plantao/assistencias-judiciarias'
				}
			]
		},
		{
			title: 'Casos',
			url: '/casos',
			icon: FileTextIcon,
			items: [
				{
					title: 'Cadastrar Novo Caso',
					url: '/casos/cadastrar-novo-caso'
				},
				{
					title: 'Meus Casos',
					url: '/casos?user=me'
				},
				{
					title: 'Gestão de Casos',
					url: '/casos'
				},
				{
					title: 'Links de Roteiro',
					url: '/casos/links-roteiro'
				}
			]
		},
		{
			title: 'Relatórios',
			url: '/relatorios',
			icon: ChartBarIcon,
			items: []
		}
	];

	let {
		ref = $bindable(null),
		collapsible = 'icon',
		user,
		...restProps
	}: ComponentProps<typeof Sidebar.Root> & { user: User } = $props();

	const visivel = (item: NavItem, urole: string) => !item.roles || item.roles.includes(urole);

	let navMainItems = $derived(
		baseNavMain
			.filter((item) => visivel(item, user.urole))
			.map((item) => ({
				...item,
				items: item.items.filter((subitem) => visivel(subitem, user.urole))
			}))
	);

	let formattedUser = $derived({
		nome: user.nome,
		email: user.email
	});
</script>

<Sidebar.Root {collapsible} {...restProps}>
	<Sidebar.Header>
		<CompanyLogo />
	</Sidebar.Header>
	<Sidebar.Content>
		<NavMain items={navMainItems} />
	</Sidebar.Content>
	<Sidebar.Footer>
		<a
			href="/termos-de-uso"
			class="px-2 text-xs text-muted-foreground group-data-[collapsible=icon]:hidden hover:underline"
		>
			Termos de uso
		</a>
		<NavUser user={formattedUser} />
	</Sidebar.Footer>
	<Sidebar.Rail />
</Sidebar.Root>
