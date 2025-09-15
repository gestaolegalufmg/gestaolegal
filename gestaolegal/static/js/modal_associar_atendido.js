document.addEventListener('DOMContentLoaded', function() {
    let currentOrientacaoId = null;
    let searchTimeout;
    
    document.addEventListener('modal:open', function(event) {
        if (event.detail.modalId === 'modalAssociarAtendido') {
            currentOrientacaoId = window.currentOrientacaoId;
            carregarAtendidos('');
        }
    });
    
    document.getElementById('buscaAtendido').addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const termo = this.value;
        
        searchTimeout = setTimeout(function() {
            carregarAtendidos(termo);
        }, 300);
    });
    
    function carregarAtendidos(termo) {
        if (!currentOrientacaoId) {
            return;
        }
        
        document.getElementById('loadingAtendidos').style.display = 'block';
        document.getElementById('tbodyAtendidos').innerHTML = '';
        
        const params = new URLSearchParams({
            termo: termo,
            orientacao_id: currentOrientacaoId
        });

        fetch(`/orientacao_juridica/buscar_atendidos?${params}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(payload => {
            const results = (payload && payload.data && payload.data.results) || [];
            const rows = results.map(r => `
                <tr>
                    <td>${r.nome}</td>
                    <td>${r.cpf || ''}</td>
                    <td>
                        <button class="btn btn-primary btn-associar" data-atendido-id="${r.id}">Associar</button>
                    </td>
                </tr>
            `).join('');
            document.getElementById('tbodyAtendidos').innerHTML = rows || '<tr><td colspan="3" class="text-center">Nenhum atendido encontrado</td></tr>';
        })
        .catch(error => {
            document.getElementById('tbodyAtendidos').innerHTML = '<tr><td colspan="3" class="text-center text-danger">Erro ao carregar atendidos</td></tr>';
        })
        .finally(() => {
            document.getElementById('loadingAtendidos').style.display = 'none';
        });
    }
    
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('btn-associar-atendido')) {
            const atendidoId = event.target.dataset.atendidoId;
            const atendidoNome = event.target.dataset.atendidoNome;
            
            if (confirm(`Deseja associar o atendido "${atendidoNome}" à orientação jurídica?`)) {
                const url = `/orientacao_juridica/associa_orientacao_juridica/${currentOrientacaoId}/${atendidoId}`;
                
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: `csrf_token=${document.querySelector('input[name="csrf_token"]').value}`
                })
                .then(response => response.json())
                .then(response => {
                    if (response.success) {
                        ModalManager.close('modalAssociarAtendido');
                        location.reload();
                    } else {
                        alert('Erro ao associar atendido: ' + response.message);
                    }
                })
                .catch(error => {
                    alert('Erro ao associar atendido');
                });
            }
        }
    });
}); 