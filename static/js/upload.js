async function upload() {
    // Envoie le fichier entré au backend
    const files = document.getElementById("imgInput").files;
    const file = files[0];

    if (file == null) {
        window.alert("Veuillez choisir une image")
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload-map", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "error") {
            console.error(data.message)
        } else {
            window.location.href = `/maps/${data.data}`;
        }
    });

    const eventSource = new EventSource("/progress")

    document.getElementById("progressContainer").style.display = "initial";

    eventSource.onmessage = function(e) {
        const [percent, message] = e.data.split("|");
        
        document.getElementById("progressContent").textContent = message;
        document.getElementById("uploadProgress").value = percent;
    }
}