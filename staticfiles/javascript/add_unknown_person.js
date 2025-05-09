const firstNameInput = document.getElementById('id_first_name');
const lastNameInput = document.getElementById('id_last_name');
document.getElementById('unknownParentBtn').addEventListener('click', function () {
    firstNameInput.value = 'Parent';
    lastNameInput.value = 'Unknown';

    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
    for (let i = 0; i < 4; i++) {
        setTimeout(function () {
            firstNameInput.style.color = 'red';
            lastNameInput.style.color = 'red';
        }, i* 600);
        setTimeout(function () {
            firstNameInput.style.color = 'black';
            lastNameInput.style.color = 'black';
        }, i* 600 + 300);
    }
  });
