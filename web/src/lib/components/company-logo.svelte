<script lang="ts">
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import GalleryVerticalEndIcon from '@lucide/svelte/icons/gallery-vertical-end';
</script>

<Sidebar.Menu>
	<Sidebar.MenuItem>
		<Sidebar.MenuButton
			size="lg"
			class="cursor-pointer data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
		>
			{#snippet child({ props })}
				<a href="/" {...props}>
					<div
						class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground"
					>
						<GalleryVerticalEndIcon class="size-4" />
					</div>
					<div class="grid flex-1 text-left text-sm leading-tight">
						<span class="truncate font-medium"> Gestão Legal </span>
					</div>
				</a>
			{/snippet}
		</Sidebar.MenuButton>
	</Sidebar.MenuItem>
</Sidebar.Menu>
