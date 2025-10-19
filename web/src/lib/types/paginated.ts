/**
 * Pagination metadata returned by the backend.
 */
export interface PaginationMeta {
	/** Total number of items across all pages */
	total: number;

	/** Current page number (1-indexed) */
	page: number;

	/** Number of items per page */
	per_page: number;

	/** Total number of pages */
	total_pages: number;

	/** Whether there is a next page */
	has_next_page: boolean;

	/** Whether there is a previous page */
	has_previous_page: boolean;
}

/**
 * Paginated response structure from the backend.
 *
 * The backend now returns pagination metadata separately from items.
 */
export interface Paginated<T> {
	/** Array of items for the current page */
	items: T[];

	/** Pagination metadata */
	pagination: PaginationMeta;
}
