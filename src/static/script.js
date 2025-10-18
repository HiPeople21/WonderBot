window.addEventListener("load", async () => {
    const createForm = document.getElementById("create-form");
    const searchForm = document.getElementById("search-form");


    createForm.addEventListener('submit', async function(event) {
        event.preventDefault();   // stop form submission
        const input = document.getElementById('guide-prompt');
        if (!input.value.trim()) { // trim removes all whitespace
            alert('Input cannot be empty or spaces only');
            input.focus();
        } else {

        }
    });

    searchForm.addEventListener('submit', async function(event) {
        event.preventDefault();   // stop form submission
        const input = document.getElementById('search');
        if (!input.value.trim()) { // trim removes all whitespace
            alert('Input cannot be empty or spaces only');
            input.focus();
        } else {
            
        }
    });
});