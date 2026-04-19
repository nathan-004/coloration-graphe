const img = document.getElementById("map")
const canvas = document.getElementById("canvas")
const ctx = canvas.getContext("2d")

img.onload = () => {
    canvas.width = img.naturalWidth
    canvas.height = img.naturalHeight

    ctx.drawImage(img, 0, 0)
}

let colors = [];
let curColors = {};

function color(centers, colors, ctx, canvas) {
    const imgd = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const pix = imgd.data;

    function getIndex(x, y) {
        return (y * canvas.width + x) * 4;
    }

    function isBlack(i) {
        return pix[i] === 0 && pix[i+1] === 0 && pix[i+2] === 0;
    }

    centers.forEach((center, idx) => {
        if (!(idx in colors)) return;

        const visited = new Set();
        let stack = [center];
        let color = colors[idx];

        while (stack.length > 0) {
            let pos = stack.pop();
            let key = `${pos[0]},${pos[1]}`;

            if (visited.has(key)) continue;
            visited.add(key);

            let i = getIndex(pos[0], pos[1]);

            // Colorier
            console.log(pos);
            pix[i] = color[0];
            pix[i+1] = color[1];
            pix[i+2] = color[2];
            pix[i+3] = 255;

            [
                [1, 0],
                [-1, 0],
                [0, 1],
                [0, -1]
            ].forEach((dir) => {

                let newX = pos[0] + dir[0];
                let newY = pos[1] + dir[1];

                if (
                    newX < 0 || newY < 0 ||
                    newX >= canvas.width ||
                    newY >= canvas.height
                ) return;

                let idx2 = getIndex(newX, newY);

                if (!visited.has(`${newX},${newY}`) && !isBlack(idx2)) {
                    stack.push([newX, newY]);
                }
            });
        }
    });

    console.log(canvas.width, canvas.height)
    ctx.putImageData(imgd, 0, 0);
}

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