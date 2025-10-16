import { browser } from '$app/environment';
import { useDebounce } from 'runed';
import { api } from '$lib/api-client';
import type { Paginated } from '$lib/types';
import { goto } from '$app/navigation';
import { page } from '$app/state';

export type PaginatedListOptions<TItem, TFilters extends Record<string, any>> = {
	endpoint: string;
	initialData: Paginated<TItem>;
	initialFilters: TFilters;
	buildParams: (filters: TFilters) => Record<string, string>;
	debounceMs?: number;
};

export function createPaginatedList<TItem, TFilters extends Record<string, any>>(
	options: PaginatedListOptions<TItem, TFilters>
) {
	const tableData = $state<Paginated<TItem>>(options.initialData);
	const filters = $state<TFilters>(options.initialFilters);

	$effect(() => {
		void loadData(filters, 1);
	});

	function updateBrowserUrl(params: URLSearchParams) {
		if (!browser) return;

		goto(`${page.url.pathname}?${params.toString()}`, {
			replaceState: true,
			noScroll: true,
			keepFocus: true
		});
	}

	async function loadData(currentFilters: TFilters, page = 1) {
		const paramData = options.buildParams(currentFilters);
		const params = new URLSearchParams(paramData);

		if (page > 1) {
			params.set('page', page.toString());
		}

		const response = await api.get(`${options.endpoint}?${params.toString()}`);

		if (!response.ok) {
			console.error(`Failed to load ${options.endpoint}`, response.statusText);
			return;
		}

		const responseData = await response.json();
		const nextTableData = responseData;

		Object.assign(tableData, nextTableData);

		const currentPage = nextTableData.page ?? page;

		if (currentPage && currentPage > 1) {
			params.set('page', currentPage.toString());
		} else {
			params.delete('page');
		}

		updateBrowserUrl(params);
	}

	const setFilters = useDebounce((newFilters: TFilters) => {
		Object.assign(filters, newFilters);
	}, options.debounceMs ?? 400);

	return {
		get tableData() {
			return tableData;
		},
		filters,
		loadData,
		setFilters
	};
}
