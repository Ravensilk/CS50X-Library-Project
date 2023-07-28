document.addEventListener('DOMContentLoaded', () => {
    const authorBtn = document.querySelector('.authorbtn');
    if (authorBtn !== null) {
        authorBtn.addEventListener('click', () => {
            authorBtn.classList.add("d-none");
            const authorInput = document.querySelector('.bookauthor');
            const authorLabel = document.querySelector('#bookauthorlabel');
            authorInput.classList.add("mt-2");
            authorInput.style.opacity = "1";
            authorInput.style.width = "100%";
            authorInput.style.position = "relative";
            authorInput.style.left = "0";
            authorInput.style.top = "0";
            authorInput.style.paddingLeft = "40px";
            authorLabel.style.visibility ="visible";
        })
    }

    const genreBtn = document.querySelector('.genrebtn');
    if (genreBtn !== null) {
        genreBtn.addEventListener('click', () => {
            genreBtn.classList.add("d-none");
            const genreInput = document.querySelector('.bookgenre');
            const genreLabel = document.querySelector('#bookgenrelabel');
            genreInput.classList.add("mt-2");
            genreInput.style.opacity = "1";
            genreInput.style.width = "100%";
            genreInput.style.position = "relative";
            genreInput.style.left = "0";
            genreInput.style.top = "0";
            genreInput.style.paddingLeft = "40px";
            genreLabel.style.visibility ="visible";
        })
    }

    const yearBtn = document.querySelector('.yearbtn');
    if (yearBtn !== null) {
        yearBtn.addEventListener('click', () => {
            yearBtn.classList.add("d-none");
            const yearInput = document.querySelector('.bookyear');
            const yearLabel = document.querySelector('#bookyearlabel');
            yearInput.classList.add("mt-2");
            yearInput.style.opacity = "1";
            yearInput.style.width = "100%";
            yearInput.style.position = "relative";
            yearInput.style.left = "0";
            yearInput.style.top = "0";
            yearInput.style.paddingLeft = "40px";
            yearLabel.style.visibility ="visible";
        })
    }

    const publisherBtn = document.querySelector('.publisherbtn');
    if (publisherBtn !== null) {
        publisherBtn.addEventListener('click', () => {
            publisherBtn.classList.add("d-none");
            const publisherInput = document.querySelector('.bookpublisher');
            const publisherLabel = document.querySelector('#bookpublisherlabel');
            publisherInput.classList.add("mt-2");
            publisherInput.style.opacity = "1";
            publisherInput.style.width = "100%";
            publisherInput.style.position = "relative";
            publisherInput.style.left = "0";
            publisherInput.style.top = "0";
            publisherInput.style.paddingLeft = "40px";
            publisherLabel.style.visibility ="visible";
        })
    }

    const bookisbnBtn = document.querySelector('.isbnbtn');
    if (bookisbnBtn !== null) {
        bookisbnBtn.addEventListener('click', () => {
            bookisbnBtn.classList.add("d-none");
            const bookisbnInput = document.querySelector('.bookisbn');
            const bookisbnLabel = document.querySelector('#bookisbnlabel');
            bookisbnInput.classList.add("mt-2");
            bookisbnInput.style.opacity = "1";
            bookisbnInput.style.width = "100%";
            bookisbnInput.style.position = "relative";
            bookisbnInput.style.left = "0";
            bookisbnInput.style.top = "0";
            bookisbnInput.style.paddingLeft = "40px";
            bookisbnLabel.style.visibility ="visible";
        }) 
    }

    const studentidBtn = document.querySelector('.studentidbtn');
    if (studentidBtn !== null) {
        studentidBtn.addEventListener('click', () => {
            studentidBtn.classList.add("d-none");
            const studentidInput = document.querySelector('.studentid');
            const studentidLabel = document.querySelector('#studentidlabel');
            studentidInput.classList.add("mt-2");
            studentidInput.style.opacity = "1";
            studentidInput.style.width = "100%";
            studentidInput.style.position = "relative";
            studentidInput.style.left = "0";
            studentidInput.style.top = "0";
            studentidInput.style.paddingLeft = "40px";
            studentidLabel.style.visibility ="visible";
        })
    }

})