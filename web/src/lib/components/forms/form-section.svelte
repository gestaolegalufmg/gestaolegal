<script lang="ts">
	let {
		title,
		children,
		columns = 'auto',
		description
	}: {
		title: string;
		children: any;
		columns?: 'auto' | '1' | '2' | '3';
		description?: string;
	} = $props();

	const gridCols = {
		auto: 'grid-cols-1 md:grid-cols-2',
		'1': 'grid-cols-1',
		'2': 'grid-cols-1 md:grid-cols-2',
		'3': 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
	};
</script>

<div class="space-y-6">
	<div class="rounded-lg border bg-card shadow-sm">
		<div class="border-b border-border px-6 py-5">
			<h3 class="text-lg font-semibold text-foreground">{title}</h3>
			{#if description}
				<p class="mt-1 text-sm text-muted-foreground">{description}</p>
			{/if}
		</div>
		<div class="p-6">
			<div class="grid gap-6 {gridCols[columns]}">
				{@render children?.()}
			</div>
		</div>
	</div>
</div>
