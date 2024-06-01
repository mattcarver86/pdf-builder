let currentImageIndex = 0;
const bookImage = document.getElementById('bookImage');
const centerLine = document.getElementById('centerLine');
const handle1 = document.getElementById('handle1');
const handle2 = document.getElementById('handle2');
const marker1 = document.getElementById('marker1');
const marker2 = document.getElementById('marker2');
const leftBoundingBox = document.getElementById('leftBoundingBox');
const rightBoundingBox = document.getElementById('rightBoundingBox');
const nextButton = document.getElementById('nextButton');
const processButton = document.getElementById('processButton');
const sidebar = document.getElementById('sidebar');

const filters=document.getElementsByClassName('filter-option');

let originalImageWidth, originalImageHeight;
let scaleFactor;

// Sort images alphabetically
images.sort();

function updateLineAndBoxes() {
    const ratio = 0.7054263566;
    const x1 = parseFloat(handle1.style.left);
    const y1 = parseFloat(handle1.style.top);
    const x2 = parseFloat(handle2.style.left);
    const y2 = parseFloat(handle2.style.top);
    const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    const angle = (Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI) - 90;

    // Find the center point between x1, x2, y1, y2
    const centerX = (x1 + x2) / 2;
    const centerY = (y1 + y2) / 2;

    // Get the angle between x1,y1 and x2,y2
    const angleAB = Math.atan2(y2 - y1, x2 - x1);

    const angleBC = angleAB + (Math.PI / 2);

    let Cx = centerX + ((length * ratio) / 2) * Math.cos(angleBC);
    let Cy = centerY + ((length * ratio) / 2) * Math.sin(angleBC);

    let C2x = centerX - ((length * ratio) / 2) * Math.cos(angleBC);
    let C2y = centerY - ((length * ratio) / 2) * Math.sin(angleBC);

    // Update markers
    marker1.style.left = `${Cx}px`;
    marker1.style.top = `${Cy}px`;

    marker2.style.left = `${C2x}px`;
    marker2.style.top = `${C2y}px`;

    centerLine.style.width = `${length}px`;
    centerLine.style.transform = `rotate(${angle}deg)`;
    centerLine.style.left = `${x1}px`;
    centerLine.style.top = `${y1}px`;

    // Calculate the height of the bounding boxes based on the image scale factor
    const boxHeight = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    const boxWidth = boxHeight * ratio;

    // Update left bounding box
    leftBoundingBox.style.width = `${boxWidth}px`;
    leftBoundingBox.style.height = `${boxHeight}px`;
    leftBoundingBox.style.left = `${Cx - (boxWidth / 2)}px`;
    leftBoundingBox.style.top = `${Cy - (boxHeight / 2)}px`;
    leftBoundingBox.style.transform = `rotate(${angle}deg)`;

    // Update right bounding box
    rightBoundingBox.style.width = `${boxWidth}px`;
    rightBoundingBox.style.height = `${boxHeight}px`;
    rightBoundingBox.style.left = `${C2x - (boxWidth / 2)}px`;
    rightBoundingBox.style.top = `${C2y - (boxHeight / 2)}px`;
    rightBoundingBox.style.transform = `rotate(${angle}deg)`;
}

function makeDraggable(handle) {
    handle.addEventListener('mousedown', function (e) {
        const startX = e.clientX;
        const startY = e.clientY;
        const startLeft = parseFloat(handle.style.left);
        const startTop = parseFloat(handle.style.top);

        function onMouseMove(e) {
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            handle.style.left = `${startLeft + dx}px`;
            handle.style.top = `${startTop + dy}px`;
            updateLineAndBoxes();
        }

        function onMouseUp() {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            saveImageState();
        }

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    });
}

makeDraggable(handle1);
makeDraggable(handle2);

function loadImage(index) {
    if (index >= 0 && index < images.length) {
        bookImage.src = `/images/${images[index]}`;
        currentImageIndex = index;
        bookImage.onload = () => {
            // Get original dimensions of the image
            const img = new Image();
            img.src = bookImage.src;
            img.onload = function () {
                originalImageWidth = img.width;
                originalImageHeight = img.height;
                const imgRect = bookImage.getBoundingClientRect();
                scaleFactor = imgRect.width / originalImageWidth;

                handle1.style.left = `${imgRect.width / 2}px`;
                handle1.style.top = `0px`;
                handle2.style.left = `${imgRect.width / 2}px`;
                handle2.style.top = `${imgRect.height}px`;
                updateLineAndBoxes();

                // Load saved state if it exists
                const currentImage = images[currentImageIndex];
                if (imageStates[currentImage]) {
                    const linePos = imageStates[currentImage].line_position;
                    handle1.style.left = `${linePos[0] * scaleFactor}px`;
                    handle1.style.top = `${linePos[1] * scaleFactor}px`;
                    handle2.style.left = `${linePos[2] * scaleFactor}px`;
                    handle2.style.top = `${linePos[3] * scaleFactor}px`;
                    updateLineAndBoxes();
                }
            }
        }

        // Highlight the thumbnail to indicate it is currently being processed
        const thumbnails = document.getElementsByClassName('thumbnail');
        Array.from(thumbnails).forEach((thumb, idx) => {
            thumb.classList.toggle('selected', idx === index);
        });
    }
}

function createThumbnails() {
    images.forEach((image, index) => {
        console.log(image);
        const holder = document.createElement('div');
        holder.className = 'thumbnail-holder';
        const thumb = document.createElement('img');
        thumb.src = `/images/${image}`;
        thumb.className = 'thumbnail';
        thumb.id = `thumb-${index}`;
        thumb.onclick = () => loadImage(index);

        if (imageStates[image]) {
            if (imageStates[image].processed) {
                holder.classList.add('processed');
            } else {
                holder.classList.add('adjusted');
            }
        }

        holder.appendChild(thumb);
        sidebar.appendChild(holder);
    });
}

function saveImageState() {
    const linePosition = [
        parseFloat(handle1.style.left) / scaleFactor,
        parseFloat(handle1.style.top) / scaleFactor,
        parseFloat(handle2.style.left) / scaleFactor,
        parseFloat(handle2.style.top) / scaleFactor
    ];
    const currentImage = images[currentImageIndex];
    imageStates[currentImage] = {
        line_position: linePosition,
        processed: false
    };

    fetch('/save_state', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image: currentImage,
            line_position: linePosition
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('State saved:', data);
        document.getElementById(`thumb-${currentImageIndex}`).parentElement.classList.add('adjusted');
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

nextButton.addEventListener('click', function () {
    loadImage(currentImageIndex + 1);
});

processButton.addEventListener('click', function () {
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Processing success:', data);
        images.forEach((image, index) => {
            if (imageStates[image] && !imageStates[image].processed) {
                document.getElementById(`thumb-${index}`).parentElement.classList.remove('adjusted');
                document.getElementById(`thumb-${index}`).parentElement.classList.add('processed');
                imageStates[image].processed = true;
            }
        });
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

function setupFilters() {
    Array.from(filters).forEach(filter => {
        console.log(filter);
        filter.addEventListener('change', function() {
            const filterClass = `hide-${filter.getAttribute('id')}`;
            if (filter.checked) {
                sidebar.classList.remove(filterClass);
            } else {
                sidebar.classList.add(filterClass);
            }
        });
    });
}

createThumbnails();
setupFilters();
loadImage(currentImageIndex);
