function deferir_caso(url) {
    document.getElementById('deferir_confirm').href = url;
    if (window.ModalManager && typeof window.ModalManager.open === 'function') {
        window.ModalManager.open('deferir');
    }
}

function indeferir_caso(url) {
    document.getElementById('indeferir_confirm').href = url;
    if (window.ModalManager && typeof window.ModalManager.open === 'function') {
        window.ModalManager.open('indeferir');
    }
}

function excluir_caso(url) {
    document.getElementById('excluir_confirm').href = url;
    if (window.ModalManager && typeof window.ModalManager.open === 'function') {
        window.ModalManager.open('excluir');
    }
}

