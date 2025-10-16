export const flattenObject = (obj: Record<string, any>): Record<string, any> => {
	return Object.entries(obj).reduce(
		(acc, [key, value]) => {
			if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
				Object.assign(acc, flattenObject(value));
			} else {
				acc[key] = value;
			}
			return acc;
		},
		{} as Record<string, any>
	);
};
