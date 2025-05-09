const parentButtons = document.getElementById("parent-display-buttons")
const siblingsButtons = document.getElementById("siblings-display-buttons")
const partnerButtons = document.getElementById("partner-display-buttons")
const childrenButtons = document.getElementById("children-display-buttons")

const buttonList = [
    parentButtons,
    siblingsButtons,
    partnerButtons,
    childrenButtons
]

const parentSection = document.getElementById("parents-list")
const siblingsSection = document.getElementById("sibling-list")
const partnerSection = document.getElementById("partner-list")
const childrenSection = document.getElementById("children-list")

const sectionList = [
    parentSection,
    siblingsSection,
    partnerSection,
    childrenSection
]
function hideSection(skipSection) {
    const section = document.getElementById(skipSection);
    
    for (let item = 0; item < sectionList.length; item++) {
        if (sectionList[item] !== section && sectionList[item].classList.contains("d-flex")) {
            sectionList[item].classList.toggle("d-flex");
        }
    }
}

function toggleButtons(idButtons) {
    const buttons = document.getElementById(idButtons);
    buttons.classList.toggle("hidden");

    for (let item = 0; item < buttonList.length; item++) {
        if (buttonList[item] !== buttons && buttonList[item].classList.contains("hidden")) {
            buttonList[item].classList.toggle("hidden");
        }
    }
    
}



function toggleSection(idSections, idButtons) {
    // Toggle the display of the section with the given id
    // and change the button text accordingly
    const section = document.getElementById(idSections);

    if (section.style.display === "none") {
        section.classList.toggle("d-flex")
    } else {
        section.classList.toggle("d-flex")
    }
    
    toggleButtons(idButtons)
    hideSection(idSections)

}