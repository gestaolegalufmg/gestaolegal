export const TIPO_EVENTO = {
	CONTATO: 'contato',
	REUNIAO: 'reuniao',
	PROTOCOLO_DE_PETICAO: 'protocolo_de_peticao',
	DILIGENCIA_EXTERNA: 'diligencia_externa',
	AUDIENCIA: 'audencia',
	CONCILIACAO: 'conciliacao',
	DECISAO_JUDICIAL: 'decisao_judicial',
	REDISTRIBUICAO_DO_CASO: 'redistribuicao_do_caso',
	ENCERRAMENTO_DO_CASO: 'encerramento_do_caso',
	DOCUMENTOS: 'documentos',
	OUTROS: 'outros'
} as const;

export const TIPO_EVENTO_VALUES = Object.values(TIPO_EVENTO);

export type TipoEvento = (typeof TIPO_EVENTO)[keyof typeof TIPO_EVENTO];

export const TIPO_EVENTO_OPTIONS = [
	{ value: TIPO_EVENTO.CONTATO, label: 'Contato' },
	{ value: TIPO_EVENTO.REUNIAO, label: 'Reunião' },
	{ value: TIPO_EVENTO.PROTOCOLO_DE_PETICAO, label: 'Protocolo de Petição' },
	{ value: TIPO_EVENTO.DILIGENCIA_EXTERNA, label: 'Diligência Externa' },
	{ value: TIPO_EVENTO.AUDIENCIA, label: 'Audiência' },
	{ value: TIPO_EVENTO.CONCILIACAO, label: 'Conciliação' },
	{ value: TIPO_EVENTO.DECISAO_JUDICIAL, label: 'Decisão Judicial' },
	{ value: TIPO_EVENTO.REDISTRIBUICAO_DO_CASO, label: 'Redistribuição do Caso' },
	{ value: TIPO_EVENTO.ENCERRAMENTO_DO_CASO, label: 'Encerramento do Caso' },
	{ value: TIPO_EVENTO.DOCUMENTOS, label: 'Documentos' },
	{ value: TIPO_EVENTO.OUTROS, label: 'Outros' }
] as const;
