export interface ViaCepResponse {
	cep: string;
	logradouro: string;
	complemento: string;
	unidade: string;
	bairro: string;
	localidade: string;
	uf: string;
	estado: string;
	regiao: string;
	ibge: string;
	gia: string;
	ddd: string;
	siafi: string;
	erro?: boolean;
}

export interface CepLookupResult {
	success: boolean;
	data?: {
		logradouro: string;
		complemento: string;
		bairro: string;
		cidade: string;
		estado: string;
	};
	error?: string;
}

/**
 * Fetches address information from ViaCEP API
 * @param cep - CEP string (can be formatted or not)
 * @returns Promise with the lookup result
 */
export async function fetchCepData(cep: string): Promise<CepLookupResult> {
	// Remove formatting from CEP
	const cleanCep = cep.replace(/\D/g, '');

	// Validate CEP format (must have 8 digits)
	if (cleanCep.length !== 8) {
		return {
			success: false,
			error: 'CEP deve conter 8 dígitos'
		};
	}

	try {
		const response = await fetch(`https://viacep.com.br/ws/${cleanCep}/json/`);

		if (!response.ok) {
			return {
				success: false,
				error: 'Erro ao consultar o CEP'
			};
		}

		const data: ViaCepResponse = await response.json();

		// Check if CEP was not found
		if (data.erro) {
			return {
				success: false,
				error: 'CEP não encontrado'
			};
		}

		// Return formatted data
		return {
			success: true,
			data: {
				logradouro: data.logradouro,
				complemento: data.complemento,
				bairro: data.bairro,
				cidade: data.localidade,
				estado: data.uf // Using UF instead of full state name
			}
		};
	} catch (error) {
		return {
			success: false,
			error: 'Erro ao consultar o CEP. Verifique sua conexão.'
		};
	}
}
