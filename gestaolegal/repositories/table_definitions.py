from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
)

metadata = MetaData()

usuarios = Table(
    "usuarios",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(80), nullable=False),
    Column("senha", String(60), nullable=False),
    Column("urole", String(50), nullable=False),
    Column("nome", String(60), nullable=False),
    Column("sexo", String(60), nullable=False),
    Column("rg", String(18), nullable=False),
    Column("cpf", String(14), nullable=False),
    Column("profissao", String(45), nullable=False),
    Column("estado_civil", String(45), nullable=False),
    Column("nascimento", Date, nullable=False),
    Column("telefone", String(18)),
    Column("celular", String(18), nullable=False),
    Column("oab", String(30)),
    Column("obs", Text),
    Column("data_entrada", Date, nullable=False),
    Column("data_saida", Date),
    Column("criado", DateTime, nullable=False),
    Column("modificado", DateTime),
    Column("criadopor", Integer, nullable=False),
    Column("matricula", String(45)),
    Column("modificadopor", Integer),
    Column("bolsista", Boolean, nullable=False),
    Column("tipo_bolsa", String(50)),
    Column("horario_atendimento", String(30)),
    Column("suplente", String(30)),
    Column("ferias", String(150)),
    Column("status", Boolean, nullable=False),
    Column("cert_atuacao_DAJ", String(3), nullable=False),
    Column("inicio_bolsa", DateTime),
    Column("fim_bolsa", DateTime),
    Column("endereco_id", Integer, ForeignKey("enderecos.id")),
    Column("chave_recuperacao", Boolean, default=False),
)

atendidos = Table(
    "atendidos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String(80)),
    Column("data_nascimento", Date),
    Column("cpf", String(14)),
    Column("cnpj", String(18)),
    Column("endereco_id", Integer, ForeignKey("enderecos.id")),
    Column("telefone", String(18)),
    Column("celular", String(18)),
    Column("email", String(80)),
    Column("estado_civil", String(80)),
    Column("como_conheceu", String(80)),
    Column("indicacao_orgao", String(80)),
    Column("procurou_outro_local", String(80)),
    Column("procurou_qual_local", String(80)),
    Column("obs", Text),
    Column("pj_constituida", String(80)),
    Column("repres_legal", Boolean),
    Column("nome_repres_legal", String(80)),
    Column("cpf_repres_legal", String(14)),
    Column("contato_repres_legal", String(18)),
    Column("rg_repres_legal", String(50)),
    Column("nascimento_repres_legal", Date),
    Column("pretende_constituir_pj", String(80)),
    Column("status", Integer),
)

orientacao_juridica = Table(
    "orientacao_juridica",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("area_direito", String(50), nullable=False),
    Column("sub_area", String(50)),
    Column("descricao", Text, nullable=False),
    Column("data_criacao", DateTime),
    Column("status", Integer, nullable=False),
    Column("id_usuario", Integer, ForeignKey("usuarios.id")),
)

enderecos = Table(
    "enderecos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("logradouro", String(100), nullable=False),
    Column("numero", String(8), nullable=False),
    Column("complemento", String(100)),
    Column("bairro", String(100), nullable=False),
    Column("cep", String(9), nullable=False),
    Column("cidade", String(100), nullable=False),
    Column("estado", String(100), nullable=False),
)

casos = Table(
    "casos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "id_usuario_responsavel", Integer, ForeignKey("usuarios.id"), nullable=False
    ),
    Column("area_direito", String(50), nullable=False),
    Column("sub_area", String(50)),
    Column("id_orientador", Integer, ForeignKey("usuarios.id")),
    Column("id_estagiario", Integer, ForeignKey("usuarios.id")),
    Column("id_colaborador", Integer, ForeignKey("usuarios.id")),
    Column("data_criacao", DateTime, nullable=False),
    Column("id_criado_por", Integer, ForeignKey("usuarios.id"), nullable=False),
    Column("data_modificacao", DateTime),
    Column("id_modificado_por", Integer, ForeignKey("usuarios.id")),
    Column("situacao_deferimento", String(50), nullable=False),
    Column("justif_indeferimento", String(280)),
    Column("status", Boolean, nullable=False),
    Column("descricao", Text),
    Column("numero_ultimo_processo", BigInteger),
)

plantao = Table(
    "plantao",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("data_abertura", DateTime),
    Column("data_fechamento", DateTime),
)

atendido_xOrientacaoJuridica = Table(
    "atendido_xOrientacaoJuridica",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("id_orientacaoJuridica", Integer, ForeignKey("orientacao_juridica.id")),
    Column("id_atendido", Integer, ForeignKey("atendidos.id")),
)

assistencias_judiciarias = Table(
    "assistencias_judiciarias",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String(150), nullable=False),
    Column("regiao", String(80), nullable=False),
    Column("areas_atendidas", String(1000), nullable=False),
    Column("endereco_id", Integer, ForeignKey("enderecos.id")),
    Column("telefone", String(18), nullable=False),
    Column("email", String(80), nullable=False, unique=True),
    Column("status", Integer, nullable=False),
)

assistenciasJudiciarias_xOrientacao_juridica = Table(
    "assistenciasJudiciarias_xOrientacao_juridica",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "id_assistencia_judiciaria", Integer, ForeignKey("assistencias_judiciarias.id")
    ),
    Column("id_orientacao_juridica", Integer, ForeignKey("orientacao_juridica.id")),
)

assistidos = Table(
    "assistidos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("id_atendido", Integer, ForeignKey("atendidos.id", ondelete="CASCADE")),
    Column("sexo", String(1), nullable=False),
    Column("profissao", String(80), nullable=False),
    Column("raca", String(20), nullable=False),
    Column("rg", String(50), nullable=False),
    Column("grau_instrucao", String(100), nullable=False),
    Column("salario", Numeric(10, 2), nullable=False),
    Column("beneficio", String(30), nullable=False),
    Column("qual_beneficio", String(30)),
    Column("contribui_inss", String(20), nullable=False),
    Column("qtd_pessoas_moradia", Integer, nullable=False),
    Column("renda_familiar", Numeric(10, 2), nullable=False),
    Column("participacao_renda", String(100), nullable=False),
    Column("tipo_moradia", String(100), nullable=False),
    Column("possui_outros_imoveis", Boolean, nullable=False),
    Column("quantos_imoveis", Integer),
    Column("possui_veiculos", Boolean, nullable=False),
    Column("possui_veiculos_obs", String(100)),
    Column("quantos_veiculos", Integer),
    Column("ano_veiculo", String(5)),
    Column("doenca_grave_familia", String(20), nullable=False),
    Column("pessoa_doente", String(50)),
    Column("pessoa_doente_obs", String(100)),
    Column("gastos_medicacao", Numeric(10, 2)),
    Column("obs", String(1000)),
)

assistido_pessoa_juridica = Table(
    "assistido_pessoa_juridica",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("id_assistido", Integer, ForeignKey("assistidos.id")),
    Column("nome_empresa", String(150)),
    Column("cnpj", String(18)),
    Column("inscricao_estadual", String(20)),
    Column("inscricao_municipal", String(20)),
    Column("nome_representante_legal", String(100)),
    Column("cpf_representante_legal", String(14)),
    Column("rg_representante_legal", String(20)),
    Column("cargo_representante_legal", String(50)),
    Column("telefone_representante_legal", String(18)),
    Column("email_representante_legal", String(80)),
    Column("endereco_empresa", String(200)),
    Column("atividade_economica", String(200)),
    Column("numero_funcionarios", Integer),
    Column("faturamento_mensal", Numeric(15, 2)),
    Column("capital_social", Numeric(15, 2)),
    Column("situacao_receita", String(50)),
    Column("observacoes", Text),
)

arquivos = Table(
    "arquivos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("titulo", String(150), nullable=False),
    Column("descricao", Text),
    Column("nome", Text, nullable=False),
)

arquivo_caso = Table(
    "arquivo_caso",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("id_arquivo", Integer, ForeignKey("arquivos.id")),
    Column("id_caso", Integer, ForeignKey("casos.id")),
    Column("data_upload", DateTime),
    Column("uploaded_by", Integer, ForeignKey("usuarios.id")),
)

arquivos_evento = Table(
    "arquivos_evento",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("id_arquivo", Integer, ForeignKey("arquivos.id")),
    Column("id_evento", Integer, ForeignKey("eventos.id")),
    Column("data_upload", DateTime),
    Column("uploaded_by", Integer, ForeignKey("usuarios.id")),
)

eventos = Table(
    "eventos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("id_caso", Integer, ForeignKey("casos.id"), nullable=False),
    Column("num_evento", Integer, default=0),
    Column("tipo", String(50), nullable=False),
    Column("descricao", Text),
    Column("arquivo", String(100)),
    Column("data_evento", Date, nullable=False),
    Column("data_criacao", DateTime, nullable=False),
    Column("id_criado_por", Integer, ForeignKey("usuarios.id"), nullable=False),
    Column("id_usuario_responsavel", Integer, ForeignKey("usuarios.id")),
    Column("status", Boolean, default=True, nullable=False),
)

processos = Table(
    "processos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("especie", String(25), nullable=False),
    Column("numero", BigInteger, unique=True),
    Column("identificacao", Text),
    Column("vara", String(200)),
    Column("link", String(1000)),
    Column("probabilidade", String(25)),
    Column("posicao_assistido", String(25)),
    Column("valor_causa_inicial", Integer),
    Column("valor_causa_atual", Integer),
    Column("data_distribuicao", Date),
    Column("data_transito_em_julgado", Date),
    Column("obs", Text),
    Column("id_caso", Integer, ForeignKey("casos.id"), nullable=False),
    Column("status", Boolean, default=True, nullable=False),
    Column(
        "id_criado_por", Integer, ForeignKey("usuarios.id"), nullable=False, default=1
    ),
)

historicos = Table(
    "historicos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("id_usuario", Integer, ForeignKey("usuarios.id"), nullable=False),
    Column("id_caso", Integer, ForeignKey("casos.id"), nullable=False),
    Column("data", DateTime, nullable=False),
)

lembretes = Table(
    "lembretes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("num_lembrete", Integer, default=0),
    Column("id_do_criador", Integer, ForeignKey("usuarios.id"), nullable=False),
    Column("id_caso", Integer, ForeignKey("casos.id"), nullable=False),
    Column("id_usuario", Integer, ForeignKey("usuarios.id"), nullable=False),
    Column("data_criacao", DateTime, nullable=False),
    Column("data_lembrete", DateTime, nullable=False),
    Column("descricao", Text, nullable=False),
    Column("status", Boolean, default=True, nullable=False),
)

notificacao = Table(
    "notificacao",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("id_executor_acao", Integer, ForeignKey("usuarios.id")),
    Column("id_usu_notificar", Integer, ForeignKey("usuarios.id")),
    Column("acao", String(200), nullable=False),
    Column("data", Date, nullable=False),
)

casos_atendidos = Table(
    "casos_atendidos",
    metadata,
    Column("id_caso", Integer, ForeignKey("casos.id", ondelete="CASCADE")),
    Column("id_atendido", Integer, ForeignKey("atendidos.id", ondelete="CASCADE")),
)

roteiro = Table(
    "roteiro",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String(100), nullable=False),
    Column("descricao", Text),
    Column("area_direito", String(50)),
    Column("ativo", Boolean, default=True),
)

registro_entrada = Table(
    "registro_entrada",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("id_atendido", Integer, ForeignKey("atendidos.id")),
    Column("data_entrada", DateTime, nullable=False),
    Column("id_usuario", Integer, ForeignKey("usuarios.id")),
    Column("observacoes", Text),
)

fila_atendidos = Table(
    "fila_atendidos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("id_atendido", Integer, ForeignKey("atendidos.id")),
    Column("id_plantao", Integer, ForeignKey("plantao.id")),
    Column("data_entrada", DateTime, nullable=False),
    Column("prioridade", Integer, default=0),
    Column("status", String(20), default="aguardando"),
    Column("observacoes", Text),
)

dia_plantao = Table(
    "dia_plantao",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("id_plantao", Integer, ForeignKey("plantao.id")),
    Column("data", Date, nullable=False),
    Column("horario_inicio", String(10)),
    Column("horario_fim", String(10)),
    Column("status", String(20), default="aberto"),
)

dias_marcados_plantao = Table(
    "dias_marcados_plantao",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("id_usuario", Integer, ForeignKey("usuarios.id")),
    Column("data", Date, nullable=False),
    Column("horario_inicio", String(10)),
    Column("horario_fim", String(10)),
    Column("observacoes", Text),
)
