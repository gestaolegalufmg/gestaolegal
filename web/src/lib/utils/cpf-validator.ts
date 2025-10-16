export function validateCPF(cpf: string): boolean {
	const cleanCpf = cpf.replace(/\D/g, '');

	if (cleanCpf.length !== 11) {
		return false;
	}

	// Check if all digits are the same (invalid CPF)
	if (/^(\d)\1{10}$/.test(cleanCpf)) {
		return false;
	}

	// Extract the 9 first digits and the 2 verification digits
	const digits = cleanCpf.split('').map(Number);
	const firstNineDigits = digits.slice(0, 9);
	const verificationDigits = digits.slice(9, 11);

	// Validate first verification digit
	const firstDigit = calculateVerificationDigit(firstNineDigits);
	if (firstDigit !== verificationDigits[0]) {
		return false;
	}

	// Validate second verification digit
	const firstTenDigits = [...firstNineDigits, firstDigit];
	const secondDigit = calculateVerificationDigit(firstTenDigits, 11);
	if (secondDigit !== verificationDigits[1]) {
		return false;
	}

	return true;
}

function calculateVerificationDigit(digits: number[], startMultiplier: number = 10): number {
	let sum = 0;
	let multiplier = startMultiplier;

	for (const digit of digits) {
		sum += digit * multiplier;
		multiplier--;
	}

	const remainder = (sum * 10) % 11;

	return remainder === 10 ? 0 : remainder;
}
