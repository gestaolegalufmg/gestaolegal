<script lang="ts" module>
	import type { BadgeVariant } from '$lib/components/ui/badge';

	export type Column = {
		header: string;
		key?: string;
		class?: string;
		type?: 'text' | 'mono' | 'date' | 'datetime' | 'badge' | 'status' | 'array' | 'tel';
		badgeMap?: Record<string | number, { text: string; variant: BadgeVariant; class?: string }>;
	};
</script>

<script lang="ts" generics="T extends { id:  number }">
	import * as Table from '$lib/components/ui/table';
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import type { Paginated } from '$lib/types';
	import type { Component } from 'svelte';
	import { cn } from '$lib/utils';
	import { goto } from '$app/navigation';
	import ChevronLeft from '@lucide/svelte/icons/chevron-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import ChevronsLeft from '@lucide/svelte/icons/chevrons-left';
	import ChevronsRight from '@lucide/svelte/icons/chevrons-right';

	type ActionButton = {
		title: string;
		href?: (item: T) => string;
		onClick?: (item: T) => void | Promise<void>;
		icon?: Component;
		show?: (item: T) => boolean;
		disabled?: (item: T) => boolean;
		variant?: 'ghost' | 'default' | 'secondary' | 'destructive';
		class?: string;
	};

	let {
		columns,
		data,
		tableClass,
		emptyText = 'Nenhum registro encontrado.',
		actions,
		onPageChange
	} = $props<{
		columns: Column[];
		data: Paginated<T>;
		tableClass?: string;
		emptyText?: string;
		actions?: { class?: string; buttons: ActionButton[] };
		onPageChange?: (page: number) => void | Promise<void>;
	}>();

	let isScrolled = $state(false);
	let scrollContainer: HTMLDivElement;

	let totalPages = $derived(Math.ceil(data.total / data.per_page));
	let startItem = $derived((data.page - 1) * data.per_page + 1);
	let endItem = $derived(Math.min(data.page * data.per_page, data.total));

	async function handlePageChange(newPage: number) {
		if (onPageChange) {
			await onPageChange(newPage);
		} else {
			const url = new URL(window.location.href);
			url.searchParams.set('page', String(newPage));
			await goto(url.toString(), { keepFocus: true, noScroll: true });
		}
	}

	function checkScroll(target: HTMLDivElement) {
		const maxScroll = target.scrollWidth - target.clientWidth;
		const hasScroll = maxScroll > 0;
		const notAtEnd = target.scrollLeft < maxScroll - 1;
		isScrolled = hasScroll && notAtEnd;
	}

	function handleScroll(event: Event) {
		checkScroll(event.currentTarget as HTMLDivElement);
	}

	$effect(() => {
		if (scrollContainer) {
			checkScroll(scrollContainer);

			const resizeObserver = new ResizeObserver(() => {
				checkScroll(scrollContainer);
			});

			resizeObserver.observe(scrollContainer);

			return () => {
				resizeObserver.disconnect();
			};
		}
	});

	function formatDate(value: string | number | Date): string {
		if (!value) return '--';
		const d = new Date(value);
		return d.toLocaleDateString('pt-BR');
	}

	function formatDateTime(value: string | number | Date): string {
		if (!value) return '--';
		const d = new Date(value);
		return (
			d.toLocaleDateString('pt-BR') +
			' ' +
			d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
		);
	}

	function formatArray(value: string[]): string {
		if (!value) return '--';
		if (value.length == 1) return value[0];

		const abbreviatedNames = value.map((item) => {
			const names = item.trim().split(/\s+/);
			if (names.length === 1) return names[0];
			const first = names[0];
			const lastInitial = names.length > 1 ? names[names.length - 1][0].toUpperCase() + '.' : '';
			return lastInitial ? `${first} ${lastInitial}` : first;
		});
		return abbreviatedNames.join(', ');
	}

	function formatTel(value: string | number): string {
		if (!value) return '--';
		const str = String(value).replace(/\D/g, '');

		// +XX (XX) X XXXX-XXXX
		const intlMobile = str.match(/^(\d{2})(\d{2})(\d{1})(\d{4})(\d{4})$/);
		if (intlMobile) {
			return `+${intlMobile[1]} (${intlMobile[2]}) ${intlMobile[3]} ${intlMobile[4]}-${intlMobile[5]}`;
		}

		// +XX (XX) XXXX-XXXX
		const intlLandline = str.match(/^(\d{2})(\d{2})(\d{4})(\d{4})$/);
		if (intlLandline) {
			return `+${intlLandline[1]} (${intlLandline[2]}) ${intlLandline[3]}-${intlLandline[4]}`;
		}

		// (XX) X XXXX-XXXX
		const mobile = str.match(/^(\d{2})(\d{1})(\d{4})(\d{4})$/);
		if (mobile) {
			return `(${mobile[1]}) ${mobile[2]} ${mobile[3]}-${mobile[4]}`;
		}

		// (XX) XXXX-XXXX
		const landline = str.match(/^(\d{2})(\d{4})(\d{4})$/);
		if (landline) {
			return `(${landline[1]}) ${landline[2]}-${landline[3]}`;
		}

		return String(value);
	}

	function getNestedValue(obj: any, path: string): any {
		return path.split('.').reduce((current, prop) => current?.[prop], obj);
	}
</script>

<div
	class="table-scroll overflow-x-auto rounded-md border"
	onscroll={handleScroll}
	bind:this={scrollContainer}
>
	<Table.Root class={cn('bg-background', tableClass)}>
		<Table.Header>
			<Table.Row>
				{#each columns as column}
					<Table.Head class={column.class}>{column.header}</Table.Head>
				{/each}
				{#if actions?.buttons?.length}
					<Table.Head
						class={cn(
							'sticky right-0 bg-background transition-[filter]',
							isScrolled && 'drop-shadow-lg',
							actions.class || 'w-[120px] text-right'
						)}>Ações</Table.Head
					>
				{/if}
			</Table.Row>
		</Table.Header>
		<Table.Body>
			{#each data.items as item (item.id)}
				<Table.Row>
					{#each columns as column}
						{#if column.type === 'mono'}
							<Table.Cell class={column.class}
								><span class="font-mono text-sm"
									>{String(getNestedValue(item, column.key) ?? '')}</span
								></Table.Cell
							>
						{:else if column.type === 'date'}
							<Table.Cell class={column.class}
								><span class="text-sm">{formatDate(getNestedValue(item, column.key))}</span
								></Table.Cell
							>
						{:else if column.type === 'datetime'}
							<Table.Cell class={column.class}
								><span class="text-sm">{formatDateTime(getNestedValue(item, column.key))}</span
								></Table.Cell
							>
						{:else if column.type === 'badge'}
							<Table.Cell class={column.class}>
								{@const value = getNestedValue(item, column.key)}
								{#if column.badgeMap && value != null && value in column.badgeMap}
									<Badge
										variant={column.badgeMap[value].variant}
										class={column.badgeMap[value].class}
									>
										{column.badgeMap[value].text}
									</Badge>
								{:else if value}
									<Badge>{String(value)}</Badge>
								{:else}
									<span class="text-sm text-muted-foreground">--</span>
								{/if}
							</Table.Cell>
						{:else if column.type === 'status'}
							<Table.Cell class={column.class}>
								{#if getNestedValue(item, column.key) === 1 || getNestedValue(item, column.key) === true}
									<Badge variant="default">Ativo</Badge>
								{:else}
									<Badge variant="secondary">Inativo</Badge>
								{/if}
							</Table.Cell>
						{:else if column.type === 'array'}
							{@const value = getNestedValue(item, column.key)}
							<Table.Cell class={column.class}
								><span class="text-sm">{Array.isArray(value) ? formatArray(value) : '--'}</span
								></Table.Cell
							>
						{:else if column.type === 'tel'}
							<Table.Cell class={column.class}
								><span class="text-sm">{formatTel(getNestedValue(item, column.key))}</span
								></Table.Cell
							>
						{:else}
							<Table.Cell class={column.class}
								><span class="text-sm">{String(getNestedValue(item, column.key) ?? '')}</span
								></Table.Cell
							>
						{/if}
					{/each}
					{#if actions?.buttons?.length}
						<Table.Cell
							class={cn(
								'sticky right-0 bg-background text-right transition-[filter]',
								isScrolled && 'drop-shadow-lg'
							)}
						>
							<div class="flex items-center justify-end gap-1">
								{#each actions.buttons as btn}
									{#if !btn.show || btn.show(item)}
										<Button
											variant={btn.variant || 'ghost'}
											size="sm"
											class={btn.class || 'h-8 w-8 p-0'}
											disabled={btn.disabled ? btn.disabled(item) : false}
											href={btn.href ? btn.href(item) : undefined}
											onclick={btn.onClick ? () => btn.onClick?.(item) : undefined}
											title={btn.title}
										>
											{#if btn.icon}
												{@const Icon = btn.icon}
												<Icon class="h-4 w-4" />
											{:else}
												{btn.title}
											{/if}
										</Button>
									{/if}
								{/each}
							</div>
						</Table.Cell>
					{/if}
				</Table.Row>
			{/each}
		</Table.Body>
	</Table.Root>

	{#if !data || data.items.length === 0}
		<div class="py-8 text-center text-muted-foreground">{emptyText}</div>
	{/if}
</div>

{#if data.total > 0}
	<div
		class="flex items-center justify-between rounded-b-md border-x border-b bg-muted/50 px-4 py-3"
	>
		<div class="text-sm text-muted-foreground">
			Mostrando <span class="font-medium">{startItem}</span> a
			<span class="font-medium">{endItem}</span>
			de <span class="font-medium">{data.total}</span> resultados
		</div>
		<div class="flex items-center space-x-2">
			<div class="mr-4 text-sm text-muted-foreground">
				Página {data.page} de {totalPages}
			</div>
			<Button
				variant="ghost"
				size="sm"
				onclick={() => handlePageChange(1)}
				disabled={data.page === 1}
				title="Primeira página"
			>
				<ChevronsLeft class="h-4 w-4" />
			</Button>
			<Button
				variant="ghost"
				size="sm"
				onclick={() => handlePageChange(data.page - 1)}
				disabled={data.page === 1}
				title="Página anterior"
			>
				<ChevronLeft class="h-4 w-4" />
			</Button>
			<Button
				variant="ghost"
				size="sm"
				onclick={() => handlePageChange(data.page + 1)}
				disabled={data.page >= totalPages}
				title="Próxima página"
			>
				<ChevronRight class="h-4 w-4" />
			</Button>
			<Button
				variant="ghost"
				size="sm"
				onclick={() => handlePageChange(totalPages)}
				disabled={data.page >= totalPages}
				title="Última página"
			>
				<ChevronsRight class="h-4 w-4" />
			</Button>
		</div>
	</div>
{/if}

<style>
	.table-scroll::-webkit-scrollbar {
		height: 8px;
	}

	.table-scroll::-webkit-scrollbar-track {
		background: hsl(var(--muted));
		border-radius: 4px;
	}

	.table-scroll::-webkit-scrollbar-thumb {
		background: hsl(var(--muted-foreground) / 0.3);
		border-radius: 4px;
	}

	.table-scroll::-webkit-scrollbar-thumb:hover {
		background: hsl(var(--muted-foreground) / 0.5);
	}

	.table-scroll {
		scrollbar-width: thin;
		scrollbar-color: hsl(var(--muted-foreground) / 0.3) hsl(var(--muted));
	}
</style>
