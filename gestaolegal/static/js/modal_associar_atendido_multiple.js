document.addEventListener('DOMContentLoaded', function() {
    let searchTimeout;
    let selectedAtendidos = [];
    
    // Listen for modal open events
    document.addEventListener('modal:open', function(event) {
        if (event.detail.modalId === 'modalAssociarAtendidoMultiple') {
            carregarAtendidos('');
        }
    });
    
    document.getElementById('buscaAtendidoMultiple').addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const termo = this.value;
        
        searchTimeout = setTimeout(function() {
            carregarAtendidos(termo);
        }, 300);
    });
    
    function carregarAtendidos(termo) {
        document.getElementById('loadingAtendidosMultiple').style.display = 'block';
        document.getElementById('tbodyAtendidosMultiple').innerHTML = '';
        
        const params = new URLSearchParams({
            termo: termo,
            orientacao_id: 0
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
                    <td><input type="checkbox" data-atendido-id="${r.id}" /></td>
                    <td>${r.nome}</td>
                    <td>${r.cpf || ''}</td>
                    <td></td>
                </tr>
            `).join('');
            document.getElementById('tbodyAtendidosMultiple').innerHTML = rows || '<tr><td colspan="4" class="text-center">Nenhum atendido encontrado</td></tr>';
            updateSelectedCount();
        })
        .catch(error => {
            document.getElementById('tbodyAtendidosMultiple').innerHTML = '<tr><td colspan="4" class="text-center text-danger">Erro ao carregar atendidos</td></tr>';
        })
        .finally(() => {
            document.getElementById('loadingAtendidosMultiple').style.display = 'none';
        });
    }
    
    document.addEventListener('change', function(event) {
        if (event.target.matches('#tbodyAtendidosMultiple input[type="checkbox"]')) {
            updateSelectedCount();
        }
        
        if (event.target.matches('#checkallMultiple')) {
            const isChecked = event.target.checked;
            const checkboxes = document.querySelectorAll('#tbodyAtendidosMultiple input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            updateSelectedCount();
        }
    });
    
    function updateSelectedCount() {
        const checkedBoxes = document.querySelectorAll('#tbodyAtendidosMultiple input[type="checkbox"]:checked');
        const allBoxes = document.querySelectorAll('#tbodyAtendidosMultiple input[type="checkbox"]');
        const checkedCount = checkedBoxes.length;
        const totalCount = allBoxes.length;
        const checkAllBox = document.getElementById('checkallMultiple');
        const button = document.getElementById('associarSelecionados');
        
        if (checkedCount === 0) {
            checkAllBox.indeterminate = false;
            checkAllBox.checked = false;
        } else if (checkedCount === totalCount) {
            checkAllBox.indeterminate = false;
            checkAllBox.checked = true;
        } else {
            checkAllBox.indeterminate = true;
        }
        
        if (checkedCount > 0) {
            button.disabled = false;
            button.textContent = `Associar Selecionados (${checkedCount})`;
        } else {
            button.disabled = true;
            button.textContent = 'Associar Selecionados';
        }
    }
    
    document.addEventListener('click', function(event) {
        if (event.target.id === 'associarSelecionados') {
            const checkedBoxes = document.querySelectorAll('#tbodyAtendidosMultiple input[type="checkbox"]:checked');
            selectedAtendidos = [];
            
            checkedBoxes.forEach(checkbox => {
                const row = checkbox.closest('tr');
                const cells = row.querySelectorAll('td');
                const atendidoId = checkbox.dataset.atendidoId;
                const atendidoNome = cells[1].textContent.trim();
                const atendidoCpf = cells[2].textContent.trim();
                const atendidoCelular = cells[3].textContent.trim();
                
                selectedAtendidos.push({
                    id: atendidoId,
                    nome: atendidoNome,
                    cpf: atendidoCpf,
                    celular: atendidoCelular
                });
            });
            
            if (selectedAtendidos.length > 0) {
                updateFormWithSelectedAtendidos();
                ModalManager.close('modalAssociarAtendidoMultiple');
            }
        }
    });
    
    function updateFormWithSelectedAtendidos() {
        const existingList = document.getElementById('lista-atendidos');
        if (existingList) {
            existingList.remove();
        }
        
        const container = document.querySelector('#atendidos > div > p');
        const newDiv = document.createElement('div');
        newDiv.id = 'lista-atendidos';
        newDiv.innerHTML = `
            <table class="table table-striped">
                <tbody></tbody>
            </table>
        `;
        container.parentNode.insertBefore(newDiv, container.nextSibling);
        
        const tableBody = newDiv.querySelector('tbody');
        selectedAtendidos.forEach(atendido => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${atendido.nome}</td>
                <td>${atendido.cpf}</td>
                <td>${atendido.celular}</td>
                <td>
                    <a href="/atendido/${atendido.id}" target="_blank" class="btn btn-sm btn-info">visualizar</a>
                </td>
            `;
            tableBody.appendChild(row);
        });
        
        const atendidosData = { id: selectedAtendidos.map(a => a.id) };
        const hiddenInput = document.createElement('input');
        hiddenInput.id = 'listaAtendidos';
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'listaAtendidos';
        hiddenInput.value = JSON.stringify(atendidosData);
        document.getElementById('form').insertBefore(hiddenInput, document.getElementById('form').firstChild);
    }
    
    // Listen for modal close events
    document.addEventListener('modal:close', function(event) {
        if (event.detail.modalId === 'modalAssociarAtendidoMultiple') {
            document.getElementById('buscaAtendidoMultiple').value = '';
            document.getElementById('tbodyAtendidosMultiple').innerHTML = '';
            const checkAllBox = document.getElementById('checkallMultiple');
            checkAllBox.checked = false;
            checkAllBox.indeterminate = false;
            const button = document.getElementById('associarSelecionados');
            button.disabled = true;
            button.textContent = 'Associar Selecionados';
        }
    });
}); 