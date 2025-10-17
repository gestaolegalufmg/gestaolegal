import { goto } from '$app/navigation';
import { page } from '$app/state';

export type PaginatedFiltersOptions<TFilters extends Record<string, any>> = {
	initialFilters: TFilters;
	buildParams: (filters: TFilters) => Record<string, string>;
};

export function usePaginatedFilters<TFilters extends Record<string, any>>(
	options: PaginatedFiltersOptions<TFilters>
) {
	const filters = $state<TFilters>(options.initialFilters);

	function updateBrowserUrl(params: URLSearchParams) {
		goto(`${page.url.pathname}?${params.toString()}`, {
			replaceState: true,
			noScroll: true,
			keepFocus: true
		});
	}

	function setFilters(newFilters: Partial<TFilters>) {
		Object.assign(filters, newFilters);
	}

	function applyFilters(args: { page?: number } = {}) {
		const { page: pageNumber = 1 } = args;
		const params = new URLSearchParams(options.buildParams(filters));

		if (pageNumber > 1) {
			params.set('page', pageNumber.toString());
		}

		updateBrowserUrl(params);
	}

	return {
		filters,
		applyFilters,
		setFilters
	};
}
