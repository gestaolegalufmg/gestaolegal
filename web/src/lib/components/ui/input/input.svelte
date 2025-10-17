<script lang="ts">
	import type { FormEventHandler, HTMLInputAttributes, HTMLInputTypeAttribute } from 'svelte/elements';
	import { cn, type WithElementRef } from '$lib/utils.js';
	import { Debounced, useDebounce } from 'runed';

	type InputType = Exclude<HTMLInputTypeAttribute, 'file'>;

	type Props = WithElementRef<
		Omit<HTMLInputAttributes, 'type'> &
			({ type: 'file'; files?: FileList } | { type?: InputType; files?: undefined })
	> & {
		debouncedValue?: string;
		debounceMs?: number;
		ondebounceinput?: FormEventHandler<HTMLInputElement> | null;
	};

	let {
		ref = $bindable(null),
		value = $bindable(),
		debouncedValue = $bindable(),
		debounceMs = 400,
		type,
		files = $bindable(),
		class: className,
		ondebounceinput,
		...restProps
	}: Props = $props();

	const debounced = new Debounced(() => value, debounceMs);
	const debouncedInputHandler = ondebounceinput ? useDebounce(ondebounceinput, debounceMs) : undefined;

	function handleInput(event: Event & { currentTarget: EventTarget & HTMLInputElement }) {
		restProps.oninput?.(event);
		debouncedInputHandler?.(event);
	}

	$effect(() => {
		debouncedValue = debounced.current;
	});
</script>

{#if type === 'file'}
	<input
		bind:this={ref}
		data-slot="input"
		class={cn(
			'flex h-9 w-full min-w-0 rounded-md border border-input bg-transparent px-3 pt-1.5 text-sm font-medium shadow-xs ring-offset-background transition-[color,box-shadow] outline-none selection:bg-primary selection:text-primary-foreground placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50 md:text-sm dark:bg-input/30',
			'focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50',
			'aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40',
			className
		)}
		type="file"
		bind:files
		bind:value
		oninput={handleInput}
		{...restProps}
	/>
{:else}
	<input
		bind:this={ref}
		data-slot="input"
		class={cn(
			'flex h-9 w-full min-w-0 rounded-md border border-input bg-background px-3 py-1 text-base shadow-xs ring-offset-background transition-[color,box-shadow] outline-none selection:bg-primary selection:text-primary-foreground placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50 md:text-sm dark:bg-input/30',
			'focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50',
			'aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40',
			className
		)}
		{type}
		bind:value
		oninput={handleInput}
		{...restProps}
	/>
{/if}
