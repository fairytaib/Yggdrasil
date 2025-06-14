document.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', function () {
        const selected = this.getAttribute('data-value');

        
        document.querySelectorAll('[data-relation]').forEach(div => {
            div.style.display = 'none';
        });

        
        const target = document.querySelector(`[data-relation="${selected}"]`);
        if (target) {
            target.style.display = 'block';
        }

        
        const toggleBtn = document.querySelector('.dropdown-toggle');
        toggleBtn.textContent = `Relation: ${selected.charAt(0).toUpperCase() + selected.slice(1)}`;

        document.getElementById("description").style.display = "none";
    });
});

