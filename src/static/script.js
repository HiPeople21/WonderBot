window.addEventListener("load", async () => {
    const pdf = document.getElementById("pdf");
    const createForm = document.getElementById("create-form");
    const searchForm = document.getElementById("search-form");
    const viewerButton = document.querySelector('a[href="#viewer"]');
    const loading = document.getElementById("loading");
    const closeCreate = document.querySelector("#create .close");


    createForm.addEventListener('submit', async function(event) {
        event.preventDefault();   // stop form submission
        const input = document.getElementById('guide-prompt');
        if (!input.value.trim()) { // trim removes all whitespace
            alert('Input cannot be empty or spaces only');
            input.focus();
        } else {
            loading.style.display = "grid";
            const formData = new FormData();
            formData.append('guide-prompt', input.value);
            formData.append('exercise-count', document.getElementById("exercise-count").value);
            formData.append('grade-level', document.getElementById("grade-level").value);

            const response = await fetch("/create", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            
            if (data["pdf_path"] === null) {  // An error occurred
                alert("Something went wrong, please try again.")
                return
            }

            loading.style.display = "none";
            const url = data["pdf_path"];

            pdf.src = `/static/${url}`;
            closeCreate.click();

            // Use timeout to give the close button on the create page enough time to fully interact
            setTimeout(() => {
                viewerButton.click();
            }, 400);

        }
    });

    searchForm.addEventListener('submit', async function(event) {
        event.preventDefault();   // stop form submission
        const input = document.getElementById('search-input');
        if (!input.value.trim()) { // trim removes all whitespace
            alert('Input cannot be empty or spaces only');
            input.focus();
        } else {

        }
    });
});