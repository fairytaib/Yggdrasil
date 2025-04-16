
document.getElementById('unknownParentBtn').addEventListener('click', function () {
    document.getElementById('id_first_name').value = 'Parent';
    document.getElementById('id_last_name').value = 'Unknown';

    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
  });
