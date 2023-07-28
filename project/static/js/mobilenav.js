document.addEventListener('DOMContentLoaded', () => {
    const menuDropdown = document.querySelector('.menuDropdown');
    const navCover = document.querySelector('.navCover')

    if (menuDropdown != null && navCover != null) {
        menuDropdown.addEventListener('click', () => {
            if (navCover.dataset.status == 'close') {
                navCover.style.marginLeft = "0";
                navCover.style.opacity = "1";
                navCover.dataset.status = 'open';
                menuDropdown.style.rotate = '1turn';
                menuDropdown.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor" class="bi bi-x me-2" viewBox="0 0 16 16"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg>';
            } else if (navCover.dataset.status == 'open') {
                navCover.style.marginLeft = "-1000px";
                navCover.style.opacity = "0";
                navCover.dataset.status = 'close';
                menuDropdown.style.rotate = '0turn';
                menuDropdown.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor" class="bi bi-list me-2" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"/></svg>';
            }
        })
    }
    
})