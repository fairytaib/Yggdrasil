function closeModal() {
    document.getElementById('modal').classList.remove('show');
    document.getElementById('modalBackdrop').classList.remove('show');
}

document.addEventListener('person-updated', function (e) {
    const personId = e.detail.id;
    const targetCard = document.querySelector(`#person-card-${personId}`);

    if (targetCard) {
        fetch(`/pov/{{ pov_id }}/edit/${personId}/`, {
                headers: {
                    'HX-Request': 'true'
                }
            })
            .then(response => response.text())
            .then(html => {
                targetCard.outerHTML = html;
                closeModal();
            });
    }
});

document.addEventListener('click', function (e) {
    if (e.target.matches('.modal') || e.target.matches('.modal-backdrop')) {
        document.querySelector('#modal').classList.remove('show');
        document.querySelector('#modalBackdrop').classList.remove('show');
    }
});