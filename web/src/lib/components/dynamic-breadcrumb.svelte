<script lang="ts">
	import { page } from '$app/state';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';

	const routeMap: Record<string, { label: string; href?: string }> = {
		'/': { label: 'Dashboard', href: '/' },
		'/usuarios': { label: 'Usuários', href: '/usuarios' },
		'/usuarios/novo-usuario': { label: 'Novo Usuário', href: '/usuarios/novo-usuario' },
		'/atendidos': { label: 'Atendidos e Assistidos', href: '/atendidos' },
		'/atendidos/cadastrar': { label: 'Cadastrar Atendido', href: '/atendidos/cadastrar' },
		'/casos': { label: 'Casos', href: '/casos' },
		'/casos/meus-casos': { label: 'Meus Casos', href: '/casos/meus-casos' },
		'/casos/cadastrar-novo-caso': {
			label: 'Cadastrar Novo Caso',
			href: '/casos/cadastrar-novo-caso'
		},
		'/casos/gestao-casos': { label: 'Gestão de Casos', href: '/casos/gestao-casos' },
		'/casos/gerenciar-roteiros': { label: 'Gerenciar Roteiros', href: '/casos/gerenciar-roteiros' },
		'/plantao': { label: 'Plantão', href: '/plantao' },
		'/plantao/atendidos-assistidos': {
			label: 'Atendidos/Assistidos',
			href: '/plantao/atendidos-assistidos'
		},
		'/plantao/confirmar-presenca': {
			label: 'Confirmar Presença',
			href: '/plantao/confirmar-presenca'
		},
		'/plantao/fila-atendimento': {
			label: 'Fila de Atendimento',
			href: '/plantao/fila-atendimento'
		},
		'/plantao/orientacoes-juridicas': {
			label: 'Orientações Jurídicas',
			href: '/plantao/orientacoes-juridicas'
		},
		'/plantao/registro-presenca': {
			label: 'Registro de Presença',
			href: '/plantao/registro-presenca'
		},
		'/arquivos': { label: 'Arquivos', href: '/arquivos' },
		'/arquivos/cadastrar-arquivo': {
			label: 'Cadastrar Arquivo',
			href: '/arquivos/cadastrar-arquivo'
		},
		'/arquivos/ver-arquivos': { label: 'Ver Arquivos', href: '/arquivos/ver-arquivos' },
		'/notificacoes': { label: 'Notificações', href: '/notificacoes' },
		'/relatorios': { label: 'Relatórios', href: '/relatorios' }
	};

	const dynamicRoutePatterns = [
		{
			pattern: /^\/usuarios\/\d+\/editar$/,
			label: 'Editar Usuário',
			parentLabel: 'Usuários',
			parentHref: '/usuarios'
		},
		{
			pattern: /^\/usuarios\/\d+$/,
			label: 'Visualizar Usuário',
			parentLabel: 'Usuários',
			parentHref: '/usuarios'
		},
		{
			pattern: /^\/usuarios\/eu$/,
			label: 'Meu Perfil',
			parentLabel: 'Usuários',
			parentHref: '/usuarios'
		},
		{
			pattern: /^\/usuarios\/eu\/editar$/,
			label: 'Editar Meu Perfil',
			parentLabel: 'Usuários',
			parentHref: '/usuarios'
		},
		{
			pattern: /^\/casos\/\d+\/editar$/,
			label: 'Editar Caso',
			parentLabel: 'Casos',
			parentHref: '/casos'
		},
		{
			pattern: /^\/casos\/\d+$/,
			label: 'Visualizar Caso',
			parentLabel: 'Casos',
			parentHref: '/casos'
		},
		{
			pattern: /^\/arquivos\/\d+\/editar$/,
			label: 'Editar Arquivo',
			parentLabel: 'Arquivos',
			parentHref: '/arquivos'
		},
		{
			pattern: /^\/arquivos\/\d+$/,
			label: 'Visualizar Arquivo',
			parentLabel: 'Arquivos',
			parentHref: '/arquivos'
		}
	];

	let breadcrumbs = $derived(generateBreadcrumbs(page.url.pathname));

	function generateBreadcrumbs(pathname: string) {
		const breadcrumbs: Array<{ label: string; href?: string }> = [
			{ label: 'Gestão Legal', href: '/' }
		];

		for (const pattern of dynamicRoutePatterns) {
			if (pattern.pattern.test(pathname)) {
				breadcrumbs.push({ label: pattern.parentLabel, href: pattern.parentHref });
				breadcrumbs.push({ label: pattern.label });
				return breadcrumbs;
			}
		}

		const segments = pathname.split('/').filter(Boolean);
		let currentPath = '';
		for (const segment of segments) {
			currentPath += `/${segment}`;
			const routeInfo = routeMap[currentPath];

			if (routeInfo) {
				breadcrumbs.push(routeInfo);
			} else {
				breadcrumbs.push({ label: segment.charAt(0).toUpperCase() + segment.slice(1) });
			}
		}

		return breadcrumbs;
	}
</script>

<Breadcrumb.Root>
	<Breadcrumb.List>
		{#each breadcrumbs as breadcrumb, index}
			<Breadcrumb.Item class={index === 0 ? 'hidden md:block' : ''}>
				{#if breadcrumb.href && index < breadcrumbs.length - 1}
					<Breadcrumb.Link href={breadcrumb.href} class="cursor-pointer">
						{breadcrumb.label}
					</Breadcrumb.Link>
				{:else}
					<Breadcrumb.Page>{breadcrumb.label}</Breadcrumb.Page>
				{/if}
			</Breadcrumb.Item>
			{#if index < breadcrumbs.length - 1}
				<Breadcrumb.Separator class={index === 0 ? 'hidden md:block' : ''} />
			{/if}
		{/each}
	</Breadcrumb.List>
</Breadcrumb.Root>
