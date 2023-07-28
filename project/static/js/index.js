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


});