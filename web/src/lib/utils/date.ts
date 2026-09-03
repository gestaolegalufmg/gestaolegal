/**
 * Date formatting helpers.
 *
 * The backend serializes datetimes in RFC-1123 GMT form (e.g. "Mon, 20 Jul 2026
 * 00:00:00 GMT"). Two different meanings are encoded the same way:
 *
 *  - Timestamps (created/modified moments) — real instants in time. Render these
 *    in the viewer's local timezone with {@link formatDateTime}.
 *  - Date-only values (a calendar date the user picked, stored at midnight UTC,
 *    e.g. a lembrete's data_lembrete) — have no time-of-day meaning. Render these
 *    in UTC with {@link formatDateOnly} so the calendar date is never shifted by
 *    the local timezone offset.
 */

const PLACEHOLDER = '—';

/** Format a calendar date (no time component) without any timezone shift. */
export function formatDateOnly(value: string | null | undefined): string {
	if (!value) return PLACEHOLDER;
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return PLACEHOLDER;
	return date.toLocaleDateString('pt-BR', {
		timeZone: 'UTC',
		day: '2-digit',
		month: '2-digit',
		year: 'numeric'
	});
}

/**
 * Convert an API date value (RFC-1123 GMT, e.g. "Thu, 02 Jul 2026 00:00:00 GMT")
 * into the ISO "YYYY-MM-DD" string the date picker / form expects. Returns
 * undefined for empty/invalid input. Without this, edit forms would send the raw
 * GMT string back and the backend would reject it with a validation error.
 */
export function toISODateInput(value: string | null | undefined): string | undefined {
	if (!value) return undefined;
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return undefined;
	const yyyy = date.getUTCFullYear();
	const mm = String(date.getUTCMonth() + 1).padStart(2, '0');
	const dd = String(date.getUTCDate()).padStart(2, '0');
	return `${yyyy}-${mm}-${dd}`;
}

/** Format a timestamp (date + time) in the viewer's local timezone. */
export function formatDateTime(value: string | null | undefined): string {
	if (!value) return PLACEHOLDER;
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return PLACEHOLDER;
	return date.toLocaleString('pt-BR', {
		day: '2-digit',
		month: '2-digit',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	});
}
