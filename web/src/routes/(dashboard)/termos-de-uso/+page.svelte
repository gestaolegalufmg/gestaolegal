<script lang="ts">
	import * as Card from '$lib/components/ui/card';

	// Texto herdado da página "Termos de uso" da versão 2.0 do Gestão Legal.
	const dadosTratados = [
		'Nome, e-mail, senha, função no sistema, sexo, data de nascimento, telefone, celular, endereço, CEP, RG, CPF, OAB, data de entrada, data de saída, bolsista (s/n), dia da semana e horário de atendimento, suplente, férias, certificado de atuação na DAJ (s/n);',
		'Cargo e registro de horário do plantão;',
		'Data, hora de entrada, hora de saída (DAJ).'
	];

	const finalidades = [
		'Permitir o contato com os estagiários, orientadores ou professores para tratar dos casos por eles acompanhados;',
		'Realizar o controle de ponto e presença dos estagiários e orientadores no plantão;',
		'Comprovar a quantidade de horas cumpridas pelos extensionistas vinculados à DAJ;',
		'Extrair informações de gestão dos casos acompanhados pela DAJ;',
		'Realização de pesquisas acadêmicas relacionadas aos atendimentos jurídicos realizados;',
		'Atendimento a normas acadêmicas de registro de horas e concessão de bolsas.'
	];

	const direitos = [
		'A confirmação da existência de tratamento de dados pessoais e acesso aos mesmos;',
		'A correção de dados pessoais incompletos, inexatos ou desatualizados;',
		'A anonimização, bloqueio ou eliminação de dados pessoais desnecessários, excessivos ou tratados em desconformidade com o disposto na LGPD;',
		'A portabilidade dos dados pessoais a outro fornecedor de serviço ou produto, observados os segredos comercial e industrial;',
		'A eliminação dos dados pessoais tratados com o consentimento do titular;',
		'A informação das entidades públicas e privadas com as quais a instituição realizou uso compartilhado de dados pessoais;',
		'Informação sobre a possibilidade de revogar ou não fornecer consentimento, bem como as consequências dessa negativa;',
		'A revisão de decisões tomadas unicamente com base em tratamento automatizado de dados pessoais que afetem seus interesses;',
		'A requisição da aplicação das normas de defesa do consumidor na tutela da proteção de seus dados, quando aplicável;',
		'A requisição de exclusão dos dados pessoais de nossas listas de comunicação ou marketing, assim você deixará de receber nossas mensagens e e-mails, caso não deseje mais isso.'
	];
</script>

<svelte:head>
	<title>Termos de uso - Gestão Legal</title>
</svelte:head>

<div class="max-w-4xl space-y-6">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Termos de uso</h1>
		<p class="mt-2 text-muted-foreground">
			Condições de utilização da plataforma, política de privacidade e política de cookies.
		</p>
	</div>

	<Card.Root>
		<Card.Header>
			<Card.Title>Termos de uso</Card.Title>
		</Card.Header>
		<Card.Content class="space-y-4 text-sm leading-relaxed">
			<p>
				Este software pertence e é operado pelo Projeto de Extensão Gestão Legal - UFMG (<a
					href="https://gestaolegal.direito.ufmg.br/"
					class="underline"
					target="_blank"
					rel="noopener">https://gestaolegal.direito.ufmg.br/</a
				>) (“Gestão Legal”). Estes Termos estabelecem os termos e condições sob os quais você,
				estagiário, orientador ou professor, deve utilizar a plataforma. Esta plataforma oferece aos
				usuários informações sobre o plantão de atendimento jurídico, casos jurídicos acompanhados
				pela DAJ e relatórios associados a dados pessoais de atendidos, assistidos, estagiários,
				orientadores e professores. Ao acessar a plataforma, você aprova que leu, entendeu e
				concorda em ficar vinculado a estes Termos.
			</p>
			<p>
				O serviço e todos os materiais nele contidos ou transferidos, incluindo, sem limitação,
				software, imagens, textos, gráficos, logotipos, patentes, marcas registradas, marcas de
				serviço, direitos autorais, fotografias, áudio, vídeos, música e todos os Direitos de
				Propriedade Intelectual relacionados a eles são de propriedade exclusiva do Gestão Legal.
				Exceto conforme explicitamente fornecido neste documento, nada nestes Termos deverá ser
				considerado como uma licença em ou sob tais Direitos de Propriedade Intelectual, e você
				concorda em não vender, licenciar, alugar, modificar, distribuir, copiar, reproduzir,
				transmitir, exibir publicamente, realizar publicamente, publicar, adaptar, editar ou criar
				trabalhos derivados.
			</p>
			<p>
				Na extensão máxima permitida pela lei aplicável, o Gestão Legal não assume nenhuma
				responsabilidade por quaisquer (i) erros; (ii) erros ou imprecisões de conteúdo; (iii) danos
				morais ou materiais, de qualquer natureza, resultantes do seu acesso ou uso do nosso
				serviço; (iv) qualquer acesso não autorizado ou uso de nossos servidores seguros e/ou toda e
				qualquer informação pessoal armazenada nele; (v) ações maliciosas de terceiros, como ataques
				de hackers, exceto se comprovada conduta culposa ou deliberada do Gestão Legal.
			</p>
			<p>
				Você concorda em indenizar e isentar o Gestão Legal de quaisquer demandas, perdas,
				responsabilidades, reclamações ou despesas (incluindo honorários advocatícios), feitas
				contra eles por qualquer terceiro devido a, ou decorrentes de, ou em conexão com o uso do
				site ou qualquer um dos serviços oferecidos no site.
			</p>
			<p>
				O usuário deverá utilizar a plataforma, que inclui todas as ações possíveis no sistema, em
				estrita observância às legislações e/ou normativas aplicáveis e/ou instruções da Diretoria
				Adjunta da DAJ.
			</p>
			<p>
				Reservamo-nos o direito de modificar estes termos de tempos em tempos, a nosso exclusivo
				critério. Portanto, você deve revisar essas páginas periodicamente. Quando alterarmos os
				Termos de maneira material, você será notificado. Seu uso continuado do site ou de nosso
				serviço após qualquer alteração constitui sua aceitação dos novos Termos. Se você não
				concordar com algum destes termos ou qualquer versão futura dos Termos, não use ou acesse
				(ou continue a acessar) o site ou o serviço.
			</p>
			<p>
				Estes Termos, os direitos e recursos aqui previstos, e todas e quaisquer reclamações e
				disputas relacionadas a ele e/ou aos serviços, serão regidos, interpretados e aplicados em
				todos os aspectos única e exclusivamente de acordo com as leis internas da República
				Federativa do Brasil. Todas e quaisquer reclamações e disputas serão apresentadas, e você
				consente que elas sejam decididas exclusivamente por um tribunal de jurisdição competente
				localizado em Belo Horizonte, Minas Gerais.
			</p>
		</Card.Content>
	</Card.Root>

	<Card.Root>
		<Card.Header>
			<Card.Title>Política de Privacidade</Card.Title>
		</Card.Header>
		<Card.Content class="space-y-4 text-sm leading-relaxed">
			<p>
				Ao se cadastrar na plataforma, você entende que coletamos e usamos suas informações pessoais
				nas formas descritas nesta Política, sob as normas de Proteção de Dados (LGPD, Lei Federal
				13.709/2018) e as demais normas do ordenamento jurídico brasileiro aplicáveis.
			</p>
			<p>São tratados os seguintes dados pessoais para o acesso à plataforma:</p>
			<ul class="list-disc space-y-1 pl-6">
				{#each dadosTratados as item}
					<li>{item}</li>
				{/each}
			</ul>
			<p>
				Ao utilizar nosso site e/ou fornecer seus dados pessoais, você está ciente do tratamento
				desses dados pessoais para as finalidades específicas a seguir descritas:
			</p>
			<ul class="list-disc space-y-1 pl-6">
				{#each finalidades as item}
					<li>{item}</li>
				{/each}
			</ul>
			<p>
				Solicitamos informações pessoais apenas quando realmente precisamos delas para lhe fornecer
				um serviço. Apenas retemos as informações coletadas pelo tempo necessário para fornecer o
				serviço solicitado. Quando armazenamos seus dados adotamos as boas práticas de segurança da
				informação para protegê-los e para evitar perdas e roubos, bem como acesso, divulgação,
				cópia, uso ou modificação não autorizados. Não compartilhamos informações de identificação
				pessoal publicamente ou com terceiros, exceto quando exigido por lei.
			</p>
			<p>
				Você poderá, através do e-mail <a href="mailto:dajlgpd@gmail.com" class="underline"
					>dajlgpd@gmail.com</a
				>, exercer todos os direitos que lhe são garantidos pela Lei 13.709/2018, tais como:
			</p>
			<ul class="list-disc space-y-1 pl-6">
				{#each direitos as item}
					<li>{item}</li>
				{/each}
			</ul>
			<p>
				Por outro lado, o usuário da plataforma, ao tratar dados pessoais de atendidos, assistidos,
				estagiários, orientadores e professores, em subordinação à DAJ, deve observar a LGPD, bem
				como normas aplicáveis ao tema, emanadas pela Autoridade Nacional de Proteção de Dados e
				demais órgãos reguladores.
			</p>
			<p>
				Os dados pessoais devem ser tratados, única e exclusivamente, para finalidades relacionadas
				a: (i) prestação de serviços de assistência judiciária gratuita à população hipossuficiente;
				(ii) promoção de atividades educacionais relacionadas à Faculdade de Direito - UFMG.
			</p>
		</Card.Content>
	</Card.Root>

	<Card.Root>
		<Card.Header>
			<Card.Title>Política de Cookies</Card.Title>
		</Card.Header>
		<Card.Content class="text-sm leading-relaxed">
			<p>
				Como é prática comum em quase todos os sites profissionais, este site usa cookies, que são
				pequenos arquivos baixados no seu computador, para melhorar sua experiência. Esta página
				descreve quais informações eles coletam, como as usamos e por que às vezes precisamos
				armazenar esses cookies. Utilizamos apenas cookies de sessão, que permitem você acessar a
				plataforma e utilizar os recursos disponibilizados. Não é possível bloquear a coleta desse
				tipo de cookie.
			</p>
		</Card.Content>
	</Card.Root>
</div>
