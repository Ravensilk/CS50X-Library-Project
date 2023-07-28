document.addEventListener('DOMContentLoaded', () => {

    let scrollBtn = document.querySelector(".backtotop");

    if (scrollBtn !== null) {
        window.onscroll = function () {
            scrollDetect()
        };

        function scrollDetect() {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                scrollBtn.style.display = 'block';
            } else {
                scrollBtn.style.display = 'none';
            }
        }

        scrollBtn.addEventListener('click', function() {
                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
        }) 
    }

    const favoriteBtns = document.querySelectorAll('.favorite-btn');

        favoriteBtns.forEach((btn) => {
            const csrf_token = document.querySelector('meta[name="csrf-token"]').content;
            const bookId = btn.dataset.bookid;
            btn.addEventListener('click', async () => {
                const response = await fetch('/addtofavorite', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf_token
                    },
                    body: JSON.stringify({bookid: bookId})
                });
                
                if (response.ok) {
                    data = await response.json();
                    if(data['message'] == 'Book added to your favorites.') {
                        btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="red" class="bi bi-heart-fill" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/></svg>';
                    }
                    else if (data['message'] == 'Book removed from your favorites.') {
                        btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-heart" viewBox="0 0 16 16"><path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01L8 2.748zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143c.06.055.119.112.176.171a3.12 3.12 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15z"/></svg>';
                    }         
                }
                else {
                    data = await response.json();
                    btn.innerHTML = "Failed to Add";
                }
            });
        });
    


    const bookContainers = document.querySelectorAll('.book-container');

    bookContainers.forEach((container) => {

        const addToCartBtn = container.querySelector('.add-to-cart-btn');
        const borrowSubmitForm = container.querySelector('.borrow-form')

        if (addToCartBtn !== null) {
            const csrf_token = document.querySelector('meta[name="csrf-token"]').content;
            const bookId = addToCartBtn.dataset.bookid;
            addToCartBtn.addEventListener('click', async () => {
                const response = await fetch('/cart', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf_token
                    },
                    body: JSON.stringify({bookid: bookId})
                });
                
                if (response.ok) {
                    data = await response.json();
                    const newSpan = document.createElement("span");
                    newSpan.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-cart3" viewBox="0 0 16 16"><path d="M0 1.5A.5.5 0 0 1 .5 1H2a.5.5 0 0 1 .485.379L2.89 3H14.5a.5.5 0 0 1 .49.598l-1 5a.5.5 0 0 1-.465.401l-9.397.472L4.415 11H13a.5.5 0 0 1 0 1H4a.5.5 0 0 1-.491-.408L2.01 3.607 1.61 2H.5a.5.5 0 0 1-.5-.5zM3.102 4l.84 4.479 9.144-.459L13.89 4H3.102zM5 12a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm7 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm-7 1a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm7 0a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/></svg><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="green" class="bi bi-check" viewBox="0 0 16 16"><path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/></svg>';
                    newSpan.className = 'd-flex flex-row align-items-center';
                    addToCartBtn.insertAdjacentElement("afterend", newSpan);
                    addToCartBtn.remove();
                    borrowSubmitForm.remove();
                }
                else {
                    data = await response.json();
                    const newSpan = document.createElement("span");
                    newSpan.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-cart3" viewBox="0 0 16 16"><path d="M0 1.5A.5.5 0 0 1 .5 1H2a.5.5 0 0 1 .485.379L2.89 3H14.5a.5.5 0 0 1 .49.598l-1 5a.5.5 0 0 1-.465.401l-9.397.472L4.415 11H13a.5.5 0 0 1 0 1H4a.5.5 0 0 1-.491-.408L2.01 3.607 1.61 2H.5a.5.5 0 0 1-.5-.5zM3.102 4l.84 4.479 9.144-.459L13.89 4H3.102zM5 12a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm7 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm-7 1a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm7 0a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/></svg><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="red" class="bi bi-x" viewBox="0 0 16 16"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg>';
                    newSpan.className = 'd-flex flex-row align-items-center';
                    addToCartBtn.insertAdjacentElement("afterend", newSpan);
                    addToCartBtn.remove();
                    borrowSubmitForm.remove();
                }
            });
        }

    }); 

    const borrowForm = document.querySelector('#borrow-form');

    if (borrowForm !== null) {
        const borrowBtn = document.querySelector('#borrow-cart');
        borrowForm.addEventListener('submit', () => {
            borrowBtn.disabled = true;
            borrowBtn.innerHTML = 'Loading...';
        });
    }

    const borrowAction = document.querySelector('#cart-actions');

    if (borrowAction !== null) {
        const submitBtn = document.querySelector('#button-submit');
        const removeBtn = document.querySelector('#button-remove');

        submitBtn.addEventListener('click', () => {
            borrowAction.action = "/borrowcart";
            borrowAction.submit();
            submitBtn.disabled = true;
            removeBtn.disabled = true;
            clearBtn.disabled = true;
        });

        removeBtn.addEventListener('click', () => {
            borrowAction.action = "/removecart";
            borrowAction.submit();
            submitBtn.disabled = true;
            removeBtn.disabled = true;
            clearBtn.disabled = true;
        });
    }

    const selectAllBtn = document.querySelector('.selectAllBtn');
    let choiceList = document.querySelectorAll('.choiceList')

    if (selectAllBtn != null && choiceList != null) {
        
        selectAllBtn.addEventListener('click', () => {
            choiceList.forEach((choice) => {
                let choiceBox = choice.querySelector('.formCheckBox');
                choiceBox.checked = true;
            });
        });

    }
});


