<script lang="ts">
	import * as Avatar from '$lib/components/ui/avatar/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { useSidebar } from '$lib/components/ui/sidebar/index.js';
	import ChevronsUpDownIcon from '@lucide/svelte/icons/chevrons-up-down';
	import LogOutIcon from '@lucide/svelte/icons/log-out';
	import { UserIcon } from '@lucide/svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';

	let { user }: { user: { nome: string; email: string } } = $props();
	const sidebar = useSidebar();

	const initials = user.nome
		.split(' ')
		.slice(0, 2)
		.map((name) => name[0])
		.join('');

	function logout() {
		if (typeof document !== 'undefined') {
			const secureFlag =
				typeof window !== 'undefined' && window.location.protocol === 'https:' ? '; Secure' : '';
			document.cookie = `auth_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT; SameSite=Strict${secureFlag}`;
		}

		toast.success('Você saiu do sistema');
		goto('/login');
	}
</script>

<Sidebar.Menu>
	<Sidebar.MenuItem>
		<DropdownMenu.Root>
			<DropdownMenu.Trigger>
				{#snippet child({ props })}
					<Sidebar.MenuButton
						size="lg"
						class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
						{...props}
					>
						<Avatar.Root class="size-8 rounded-lg">
							<Avatar.Fallback class="rounded-lg">{initials}</Avatar.Fallback>
						</Avatar.Root>
						<div class="grid flex-1 text-left text-sm leading-tight">
							<span class="truncate font-medium">{user.nome}</span>
							<span class="truncate text-xs">{user.email}</span>
						</div>
						<ChevronsUpDownIcon class="ml-auto size-4" />
					</Sidebar.MenuButton>
				{/snippet}
			</DropdownMenu.Trigger>
			<DropdownMenu.Content
				class="w-(--bits-dropdown-menu-anchor-width) min-w-56 rounded-lg"
				side={sidebar.isMobile ? 'bottom' : 'right'}
				align="end"
				sideOffset={4}
			>
				<DropdownMenu.Label class="p-0 font-normal">
					<div class="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
						<Avatar.Root class="size-8 rounded-lg">
							<Avatar.Fallback class="rounded-lg">{initials}</Avatar.Fallback>
						</Avatar.Root>
						<div class="grid flex-1 text-left text-sm leading-tight">
							<span class="truncate font-medium">{user.nome}</span>
							<span class="truncate text-xs">{user.email}</span>
						</div>
					</div>
				</DropdownMenu.Label>
				<DropdownMenu.Separator />
				<DropdownMenu.Group>
					<DropdownMenu.Item>
						<a class="flex items-center gap-2" href="/usuarios/eu">
							<UserIcon />
							Meu Perfil
						</a>
					</DropdownMenu.Item>
				</DropdownMenu.Group>
				<DropdownMenu.Separator />
				<DropdownMenu.Item>
					{#snippet child({ props })}
						<button
							type="button"
							class="flex w-full cursor-pointer items-center gap-2"
							onclick={logout}
							{...props}
						>
							<LogOutIcon />
							Log out
						</button>
					{/snippet}
				</DropdownMenu.Item>
			</DropdownMenu.Content>
		</DropdownMenu.Root>
	</Sidebar.MenuItem>
</Sidebar.Menu>
