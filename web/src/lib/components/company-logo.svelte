<script lang="ts">
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
</script>

<Sidebar.Menu>
	<Sidebar.MenuItem>
		<Sidebar.MenuButton
			size="lg"
			class="cursor-pointer data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
		>
			{#snippet child({ props })}
				<a href="/" {...props}>
					<img
						src="/capivara-avatar.png"
						alt=""
						class="aspect-square size-8 shrink-0 rounded-lg object-cover"
					/>
					<div class="grid flex-1 text-left text-sm leading-tight">
						<span class="truncate font-medium"> Gestão Legal </span>
					</div>
				</a>
			{/snippet}
		</Sidebar.MenuButton>
	</Sidebar.MenuItem>
</Sidebar.Menu>
