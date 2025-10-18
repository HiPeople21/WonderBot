window.addEventListener("load", async () => {
    const pdfViewer = document.getElementById("pdf");
    const createForm = document.getElementById("create-form");
    const searchInput = document.getElementById("search-input");
    const viewerButton = document.querySelector('a[href="#viewer"]');
    const loading = document.getElementById("loading");
    const closeCreate = document.querySelector("#create .close");
    const closeList = document.querySelector("#list .close");
    const pdfsList = document.getElementById("pdfs-list");


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

            pdfViewer.src = `/static/pdfs/${url}`;
            closeCreate.click();

            // Use timeout to give the close button on the create page enough time to fully interact
            setTimeout(() => {
                viewerButton.click();
            }, 400);

        }
    });

    searchInput.addEventListener('input', async function(event) {
        if (!searchInput.value.trim()) { // trim removes all whitespace
            for (const el of pdfsList.children) {
                el.classList.remove("hidden");
            }
        } else {
            for (const el of pdfsList.children) {
                if (!el.textContent.toLowerCase().includes(searchInput.value.toLowerCase())) {
                    el.classList.add("hidden");
                } else {
                    el.classList.remove("hidden");
                }
            }
        }
    });

    const response = await fetch("/list", {
        method: "POST",
    });

    const data = await response.json();
    for (const pdf of data) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        const a = document.createElement("a");
        a.textContent = pdf;
        a.href = "#";
        td.appendChild(a);
        tr.appendChild(td);
        pdfsList.appendChild(tr);

        tr.addEventListener("click", () => {
            const url = pdf;

            pdfViewer.src = `/static/pdfs/${url}`;
            closeList.click();

            // Use timeout to give the close button on the create page enough time to fully interact
            setTimeout(() => {
                viewerButton.click();
            }, 400);
        });
    }
});