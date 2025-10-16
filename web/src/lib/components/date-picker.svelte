<script lang="ts">
	import Calendar from '$lib/components/ui/calendar/calendar.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import ChevronDownIcon from '@lucide/svelte/icons/chevron-down';
	import {
		CalendarDate,
		DateFormatter,
		getLocalTimeZone,
		today,
		type DateValue
	} from '@internationalized/date';
	import * as Popover from './ui/popover';
	import { FormFieldErrors, FormDescription } from './ui/form';

	let {
		id = $bindable(),
		label,
		value = $bindable(),
		placeholder,
		...props
	}: {
		id: string;
		label: string;
		value?: string | null;
		placeholder?: string;
		[key: string]: any;
	} = $props();

	let open = $state(false);

	let dateFormatter = new DateFormatter('pt-BR', {
		dateStyle: 'long'
	});

	let date = $derived.by(() => {
		if (!value) return undefined;

		const dateObj = new Date(value);
		return dateObj
			? new CalendarDate(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate())
			: undefined;
	});
</script>

<div class="flex flex-col gap-3">
	<Popover.Root bind:open>
		<Popover.Trigger id="{id}-date">
			{#snippet child({ props })}
				<Button {...props} variant="outline" class="w-fit min-w-48 justify-between font-normal">
					{date ? dateFormatter.format(date.toDate(getLocalTimeZone())) : placeholder}
					<ChevronDownIcon />
				</Button>
			{/snippet}
		</Popover.Trigger>
		<Popover.Content class="w-auto overflow-hidden p-0" align="start">
			<Calendar
				type="single"
				bind:value={date as DateValue}
				captionLayout="dropdown"
				onValueChange={(v) => {
					if (v) {
						value = v.toString();
					} else {
						value = '';
					}
				}}
				calendarLabel={label}
				minValue={new CalendarDate(1900, 1, 1)}
				maxValue={today(getLocalTimeZone())}
			/>
		</Popover.Content>
	</Popover.Root>
	<input hidden {value} name={props.name} />
</div>
