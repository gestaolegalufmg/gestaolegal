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
	<div class="bg-card rounded-lg border p-6">
		<h2 class="text-lg font-semibold mb-4">Acesso Rápido</h2>
		<div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
			{#each buttonConfigs as buttonConfig}
				<Button
					href={buttonConfig.href}
					variant="outline"
					size="sm"
					class="h-16 flex-col gap-2 p-3 hover:bg-primary hover:text-primary-foreground transition-colors"
				>
					<buttonConfig.icon class="w-6 h-6" />
					<span class="text-xs font-medium whitespace-normal break-words text-center"
						>{buttonConfig.label}</span
					>
				</Button>
			{/each}
		</div>
	</div>
</div>
