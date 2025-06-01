document.querySelectorAll('.dropdown-item').forEach(item => {
  item.addEventListener('click', function () {
    const selected = this.getAttribute('data-value');

    // Alle Relationen ausblenden
    document.querySelectorAll('[data-relation]').forEach(div => {
      div.style.display = 'none';
    });

    // Ziel-Relation anzeigen
    const target = document.querySelector(`[data-relation="${selected}"]`);
    if (target) {
      target.style.display = 'block';
    }

    // Optional: Button-Label ändern
    const toggleBtn = document.querySelector('.dropdown-toggle');
    toggleBtn.textContent = `Relation: ${selected.charAt(0).toUpperCase() + selected.slice(1)}`;
  });
});
