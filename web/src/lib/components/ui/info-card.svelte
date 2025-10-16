<script lang="ts">
	import Card from './card/card.svelte';
	import CardHeader from './card/card-header.svelte';
	import CardTitle from './card/card-title.svelte';
	import CardContent from './card/card-content.svelte';
	import Separator from './separator/separator.svelte';

	interface InfoItem {
		label: string;
		value: string | number | boolean | null | undefined;
		formatter?: (value: any) => string;
	}

	let {
		title,
		items
	}: {
		title: string;
		items: InfoItem[];
	} = $props();

	function formatValue(item: InfoItem): string {
		if (item.value === null || item.value === undefined) {
			return 'N/A';
		}
		if (item.formatter) {
			return item.formatter(item.value);
		}
		if (typeof item.value === 'boolean') {
			return item.value ? 'Sim' : 'Não';
		}
		return String(item.value);
	}
</script>

<Card class="p-3">
	<CardHeader class="border-b-1 px-2">
		<CardTitle class="text-lg font-semibold text-foreground">{title}</CardTitle>
	</CardHeader>
	<CardContent class="flex flex-col space-y-2 gap-y-2 px-2">
		{#each items as item}
			<div class="flex items-center justify-between">
				<div class="text-xs font-medium tracking-wide text-muted-foreground uppercase">
					{item.label}
				</div>
				<div class="text-sm font-medium text-foreground">
					{formatValue(item)}
				</div>
			</div>
		{/each}
	</CardContent>
</Card>
