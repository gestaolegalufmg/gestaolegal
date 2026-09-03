<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import { podeVer, type ItemComPapeis } from '$lib/utils/permissoes';
	import BellIcon from '@lucide/svelte/icons/bell';
	import BriefcaseIcon from '@lucide/svelte/icons/briefcase';
	import CalendarDaysIcon from '@lucide/svelte/icons/calendar-days';
	import ChartBarIcon from '@lucide/svelte/icons/bar-chart-3';
	import ClockIcon from '@lucide/svelte/icons/clock';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import FolderIcon from '@lucide/svelte/icons/folder';
	import UserIcon from '@lucide/svelte/icons/user';
	import UserCogIcon from '@lucide/svelte/icons/user-cog';
	import UsersIcon from '@lucide/svelte/icons/users';
	import type { Component } from 'svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	type Atalho = ItemComPapeis & {
		href: string;
		icon: Component<any>;
		label: string;
	};

	// Os papéis repetem os da sidebar: quem não acessa a tela não vê o atalho.
	const atalhos: Atalho[] = [
		{ href: '/casos', icon: BriefcaseIcon, label: 'Casos' },
		{ href: '/casos?user=me', icon: UserIcon, label: 'Meus Casos' },
		{ href: '/plantao/escala', icon: CalendarDaysIcon, label: 'Plantão' },
		{ href: '/plantao/fila-atendimento', icon: ClockIcon, label: 'Atendimento' },
		{ href: '/plantao/atendidos-assistidos', icon: UsersIcon, label: 'Atendidos/Assistidos' },
		{ href: '/plantao/orientacoes-juridicas', icon: FileTextIcon, label: 'Ori. Jurídicas' },
		{ href: '/notificacoes', icon: BellIcon, label: 'Notificações' },
		{ href: '/arquivos', icon: FolderIcon, label: 'Arquivos' },
		{
			href: '/relatorios',
			icon: ChartBarIcon,
			label: 'Relatórios',
			roles: ['admin', 'orient', 'colab_ext']
		},
		{ href: '/usuarios', icon: UserCogIcon, label: 'Usuários', roles: ['admin'] }
	];

	const visiveis = $derived(atalhos.filter((atalho) => podeVer(atalho, data.me.urole)));
</script>

<div class="flex flex-1 flex-col gap-3">
	<div class="rounded-lg border bg-card p-6">
		<h2 class="mb-4 text-lg font-semibold">Acesso Rápido</h2>
		<div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
			{#each visiveis as atalho (atalho.href)}
				<Button
					href={atalho.href}
					variant="outline"
					size="sm"
					class="relative h-16 flex-col gap-2 p-3 transition-colors hover:bg-primary hover:text-primary-foreground"
				>
					<atalho.icon class="h-6 w-6" />
					<span class="text-center text-xs font-medium break-words whitespace-normal"
						>{atalho.label}</span
					>
					{#if atalho.href === '/notificacoes' && data.naoLidas > 0}
						<span
							class="absolute top-1 right-1 rounded-full bg-primary px-1.5 py-0.5 text-[10px] leading-none font-semibold text-primary-foreground"
							title="{data.naoLidas} não lida(s)"
						>
							{data.naoLidas}
						</span>
					{/if}
				</Button>
			{/each}
		</div>
	</div>
</div>
