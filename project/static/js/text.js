document.addEventListener('DOMContentLoaded', () => {

    const descContainers = document.querySelectorAll('.description');

        descContainers.forEach((container) => {

            const descText = container.querySelector('.descriptionText');
            const descBtn = container.querySelector('.descriptionBtn');
            const maxLength = 100;

            if (descText !== null) {

                const truncatedText = descText.innerHTML.slice(0, maxLength);
                const remainingText = descText.innerHTML.slice(maxLength);

                if (descText.innerHTML.length > maxLength) {
                    descText.innerHTML = truncatedText + '...';
                    descBtn.style.display = 'inline'; 
                }
                else {
                    descBtn.style.display = 'none';
                }

                descBtn.addEventListener('click', () => {
                    if (descText.innerHTML === truncatedText + '...') {
                        descText.innerHTML = truncatedText + remainingText;
                        descBtn.innerHTML = 'See Less';
                    }
                    
                    else {
                            descText.innerHTML = truncatedText + '...';
                            descBtn.innerHTML = 'See More';
                        }
                });
            }

        });

    }); 

