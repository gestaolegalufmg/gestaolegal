// Global AJAX loading handlers
let activeAjaxRequests = 0;

function showLoading() {
    document.getElementById('conteudoPagina').style.display = 'none';
    document.getElementById('loadingGIF').style.display = 'block';
}

function hideLoading() {
    activeAjaxRequests--;
    if (activeAjaxRequests === 0) {
        document.getElementById('loadingGIF').style.display = 'none';
        document.getElementById('conteudoPagina').style.display = 'block';
    }
}

// Override fetch to track AJAX requests
const originalFetch = window.fetch;
window.fetch = function(...args) {
    activeAjaxRequests++;
    showLoading();
    return originalFetch.apply(this, args)
        .finally(() => hideLoading());
};

document.getElementById("dataProcurada").addEventListener("change", function(){
    let nova_data = this.value;
    const tabela_presenca = document.querySelector("#tabelaPresenca tbody");
    const tabela_plantao = document.querySelector("#tabelaPlantao tbody");
    const conteudo_presenca = document.getElementById("conteudoPresenca");
    const conteudo_plantao = document.getElementById("conteudoPlantao");
    const sem_presenca = document.getElementById("semPresenca");
    const sem_plantao = document.getElementById("semPlantao");
    
    const csrftoken = document.querySelector('meta[name=csrf-token]').getAttribute('content');

    fetch(document.getElementById("hdnAjaxBuscaPresencasData").value, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=UTF-8',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            nova_data: nova_data
        })
    })
    .then(response => response.json())
    .then(result => {
        tabela_presenca.innerHTML = '';
        tabela_plantao.innerHTML = '';
        conteudo_presenca.style.display = 'none';
        conteudo_plantao.style.display = 'none';

        if(result.tem_presenca){
            conteudo_presenca.style.display = 'block';
            sem_presenca.style.display = 'none';

            for(let i = 0; i < result.presencas.length; i++){
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${result.presencas[i].Nome}</td>
                    <td>${result.presencas[i].Cargo}</td>
                    <td>${result.presencas[i].Entrada}</td>
                    <td>${result.presencas[i].Saida}</td>
                    <td>
                        <div class="col-lg-6 d-flex justify-content-center">
                            <input class="confirmacao" type="radio" name="presenca_${result.presencas[i].IdPresenca}" value="confirmar">
                        </div>
                    </td>
                    <td>
                        <div class="col-lg-6 d-flex justify-content-center">
                            <input class="confirmacao" type="radio" name="presenca_${result.presencas[i].IdPresenca}" value="divergencia">
                        </div>
                    </td>
                    <td>
                        <div class="col-lg-6 d-flex justify-content-center">
                            <input class="confirmacao" type="radio" name="presenca_${result.presencas[i].IdPresenca}" value="ausencia">
                        </div>
                    </td>
                `;
                tabela_presenca.appendChild(row);
            }
        }
        else{
            sem_presenca.style.display = 'block';
        }

        if(result.tem_plantao){
            sem_plantao.style.display = 'none';
            conteudo_plantao.style.display = 'block';

            for(let i = 0; i < result.plantoes.length; i++){  
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${result.plantoes[i].Nome}</td>
                    <td>${result.plantoes[i].Cargo}</td>
                    <td>
                        <div class="col-lg-6 d-flex justify-content-center">
                            <input class="confirmacao" type="radio" name="plantao_${result.plantoes[i].IdPlantao}" value="confirmar">
                        </div>
                    </td>
                    <td>
                        <div class="col-lg-6 d-flex justify-content-center">
                            <input class="confirmacao" type="radio" name="plantao_${result.plantoes[i].IdPlantao}" value="divergencia">
                        </div>
                    </td>
                    <td>
                        <div class="col-lg-6 d-flex justify-content-center">
                            <input class="confirmacao" type="radio" name="plantao_${result.plantoes[i].IdPlantao}" value="ausencia">
                        </div>
                    </td>
                `;
                tabela_plantao.appendChild(row);
            }
        }
        else{
            sem_plantao.style.display = 'block';
        }
    })
    .catch(error => console.error('Error:', error));
});