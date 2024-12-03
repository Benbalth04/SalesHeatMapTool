// References
const downloadBtn = document.getElementById('download-btn');
const mapContainer = document.getElementById('map-container');
const downloadPopup = document.getElementById('download-popup');
const fileSizeDisplay = document.getElementById('file-size');
const startDownloadBtn = document.getElementById('start-download-btn');
const closePopupBtn = document.getElementById('close-popup-btn');
const defaultHtmlFilePath = '../maps/generated_map.html';

// Function to show/hide the download button
function toggleDownloadButton() {
    if (mapContainer.children.length > 0) {
        downloadBtn.style.display = 'block';
    } else {
        downloadBtn.style.display = 'none';
    }
}

// Show the popup when the download button is clicked
downloadBtn.addEventListener('click', async () => {
    const htmlSize = await estimateHtmlFileSize(defaultHtmlFilePath);
    fileSizeDisplay.textContent = `Estimated size: ${htmlSize} MB` 
    downloadPopup.style.display = 'flex';
});

// Hide the popup when cancel is clicked
closePopupBtn.addEventListener('click', () => {
    downloadPopup.style.display = 'none';
});


// Start download when the final button is clicked
startDownloadBtn.addEventListener('click', async () => {
    downloadFile(defaultHtmlFilePath, 'map.html');
    downloadPopup.style.display = 'none';
});

function downloadFile(filePath, fileName) {
    const a = document.createElement('a');
    a.href = filePath;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

async function estimateHtmlFileSize(filePath) {
    try {
        const response = await fetch(filePath, { method: 'HEAD' });
        const sizeInBytes = response.headers.get('Content-Length');
        return (sizeInBytes / 1024 / 1024).toFixed(2); // Convert to MB
    } catch (error) {
        console.error('Error estimating HTML file size:', error);
        return 'Unknown';
    }
}

// Monitor changes in the map container to toggle the button
new MutationObserver(toggleDownloadButton).observe(mapContainer, { childList: true });
