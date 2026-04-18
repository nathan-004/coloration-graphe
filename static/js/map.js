let colors = [];

async function handleChangeRadio (event) {
    const algo = event.target.value;

    colors = await getColors(ID, algo);
}

async function getColors(id, algo) {
    const res = await fetch("/color", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            id: id,
            algo: algo
        })
    });

    const data = await res.json();
    
    if (data.status === "error") {
        console.error(data.message)
    } else {
        return data.data;
    }
}

document.querySelectorAll("input[name='algo']").forEach((input) => {
    input.addEventListener("change", handleChangeRadio);
});

async function initColors() {
    colors = await getColors(ID, "random");
}

initColors();