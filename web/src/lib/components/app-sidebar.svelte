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

	const baseNavMain = [
		{
			title: 'Gestão de Usuários',
			url: '/usuarios',
			icon: UsersIcon,
			isActive: true,
			items: []
		},
		{
			title: 'Plantão',
			url: '/plantao',
			icon: ClockIcon,
			items: [
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
					title: 'Gestão de Casos',
					url: '/casos'
				}
			]
		}
	];

	let {
		ref = $bindable(null),
		collapsible = 'icon',
		user,
		...restProps
	}: ComponentProps<typeof Sidebar.Root> & { user: User } = $props();

	let navMainItems = $derived(
		user.urole === 'admin' ? baseNavMain : baseNavMain.filter((item) => item.url !== '/usuarios')
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
		<NavUser user={formattedUser} />
	</Sidebar.Footer>
	<Sidebar.Rail />
</Sidebar.Root>
