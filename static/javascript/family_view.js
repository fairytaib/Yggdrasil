// function toggleButtonText(id){
//     // Toggle the text of the button with the given id
//     const button = document.getElementById(id);
//     if (button.innerHTML === "Show") {
//         button.innerHTML = "Hide";
//     } else {
//         button.innerHTML = "Show";
//     }
// }

function toggleSection(id) {
    // Toggle the display of the section with the given id
    // and change the button text accordingly
    const section = document.getElementById(id);
    if (section.style.display === "none") {
        section.style.display = "block";
    } else {
        section.style.display = "none";
    }
}

