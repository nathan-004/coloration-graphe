const img = document.getElementById("map")
const canvas = document.getElementById("canvas")
const ctx = canvas.getContext("2d")

img.onload = () => {
    canvas.width = img.naturalWidth
    canvas.height = img.naturalHeight

    ctx.drawImage(img, 0, 0)
}

let steps = 0;
let colors = [];
let regions = {};

function color(centers, colors, ctx, canvas) {
    const imgd = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const pix = imgd.data;

    function getIndex(x, y) {
        return (y * canvas.width + x) * 4;
    }

    function isBlack(i) {
        return pix[i] <= 100 && pix[i+1] <= 100 && pix[i+2] <= 100;
    }
	console.log(isBlack(0), isBlack(getIndex(657, 152)));
	
	let calcStart = new Date();
	
    centers.forEach((center, idx) => {
        if (!(idx in colors)) return
		let color = colors[idx];
		
		if (idx in regions) {
			let vals = regions[idx];
			
			vals.forEach((pos) => {
				let i = getIndex(pos[0], pos[1]);
				
				pix[i] = color[0];
				pix[i+1] = color[1];
				pix[i+2] = color[2];
				pix[i+3] = 255;
			});
			
			ctx.putImageData(imgd, 0, 0);
			
			return
		}

        const visited = new Set();
        let stack = [center];
		let curRegion = [];
		
        while (stack.length > 0) {
            let pos = stack.pop();
			pos = [Math.round(pos[0]), Math.round(pos[1])];
			curRegion.push(pos);
            let key = `${pos[0]},${pos[1]}`;

            if (visited.has(key)) continue;
            visited.add(key);

            let i = getIndex(pos[0], pos[1]);
			
			if (isBlack(i)) continue;

            // Colorier
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
		regions[idx] = curRegion;
		// console.log(visited);
    });
	
	let calcEnd = new Date();
	
	console.log(`Durée calculs : ${calcEnd.getTime() - calcStart.getTime()}ms`);

    console.log(canvas.width, canvas.height)
	
	let colorStart = new Date();
    ctx.putImageData(imgd, 0, 0);
	let colorEnd = new Date();
	console.log(`Durée coloriage : ${colorEnd.getTime() - colorStart.getTime()}ms`);
}

async function handleChangeRadio (event) {
    const algo = event.target.value;

    colors = await getColors(ID, algo);
	steps = 0;
	update();
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

function getCurrentColors(steps) {
	let currentColors = {};
	
	for (let i = 0; i < steps; i++) {
		const s = colors[i];
		Object.keys(s).forEach((k) => {
			currentColors[k] = [s[k][0] * 255, s[k][1] * 255, s[k][2] * 255];
		});
	}
	
	for (let i = 0; i < colors.length; i++) {
		if (!(i in currentColors)) {
			currentColors[i] = [255, 255, 255];
		}
	}
	
	return currentColors;
}

function update() {
	if (colors.length == 0) {
		window.alert("En attente de réponse du serveur.");
		return
	}
	
	color(CENTERS, getCurrentColors(steps), ctx, canvas);
}

function max(a, b) {
	if (a > b) {
		return a
	}
	else {
		return b
	}
}

function min(a, b) {
	if (a < b) {
		return a
	}
	else {
		return b
	}
}

function updateStep(variation) {
	steps += variation;
	steps = max(min(steps, colors.length), 0)
	update();
}

async function initColors() {
    colors = await getColors(ID, "random");
}

initColors();