<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import BriefcaseIcon from '@lucide/svelte/icons/briefcase';
	import UsersIcon from '@lucide/svelte/icons/users';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import { Building2Icon, ClockIcon } from '@lucide/svelte';

	const buttonConfigs = [
		{
			href: '/casos',
			icon: BriefcaseIcon,
			label: 'Casos'
		},
		{
			href: '/plantao/fila-atendimento',
			icon: ClockIcon,
			label: 'Atendimento'
		},
		{
			href: '/plantao/atendidos-assistidos',
			icon: UsersIcon,
			label: 'Atendidos/Assistidos'
		},

		{
			href: '/plantao/orientacoes-juridicas',
			icon: FileTextIcon,
			label: 'Ori. Jurídicas'
		},

		{
			href: '/usuarios',
			icon: UsersIcon,
			label: 'Usuários'
		}
	];
</script>

<div class="flex flex-1 flex-col gap-3">
	<div class="rounded-lg border bg-card p-6">
		<h2 class="mb-4 text-lg font-semibold">Acesso Rápido</h2>
		<div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
			{#each buttonConfigs as buttonConfig}
				<Button
					href={buttonConfig.href}
					variant="outline"
					size="sm"
					class="h-16 flex-col gap-2 p-3 transition-colors hover:bg-primary hover:text-primary-foreground"
				>
					<buttonConfig.icon class="h-6 w-6" />
					<span class="text-center text-xs font-medium break-words whitespace-normal"
						>{buttonConfig.label}</span
					>
				</Button>
			{/each}
		</div>
	</div>
</div>
