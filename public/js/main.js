// Select dropdowns and button
const resolutionDropdown = document.getElementById('resolution-dropdown');
const yearDropdown = document.getElementById('year-dropdown');
const countryDropdown = document.getElementById('country-dropdown');
const stateDropdown = document.getElementById('state-dropdown');
const generateMapBtn = document.getElementById('generate-map-btn');
const mapContainer = document.getElementById('map-container');

// Function to check if all dropdowns have been selected
function checkSelections() {
    if (
        resolutionDropdown.value &&
        yearDropdown.value &&
        countryDropdown.value &&
        stateDropdown.value
    ) {
        generateMapBtn.disabled = false;
    } else {
        generateMapBtn.disabled = true;
    }
}

// Add event listeners to dropdowns
resolutionDropdown.addEventListener('change', checkSelections);
yearDropdown.addEventListener('change', checkSelections);
countryDropdown.addEventListener('change', checkSelections);
stateDropdown.addEventListener('change', checkSelections);

generateMapBtn.addEventListener('click', async () => {
    const resolution = resolutionDropdown.value;
    const year = yearDropdown.value;
    const country = countryDropdown.value;
    const state = stateDropdown.value;

    // Prepare the request payload
    const payload = {
        resolution,
        year,
        country,
        state,
    };

    // Call the backend API
    try {
        const response = await fetch('/api/generate-map', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const htmlFilePath = data.htmlFilePath;

         // Create the iframe to load the generated map
         const iframe = document.createElement('iframe');
         iframe.src = htmlFilePath;
         iframe.width = "100%";
         iframe.height = "100%";
 
         // Clear the previous content (if any) and append the iframe to the container
         mapContainer.innerHTML = '';
         mapContainer.appendChild(iframe);

    } catch (error) {
        console.error(error);
        mapContainer.innerHTML = `<p>An unexpected error occurred. (${error.message})</p>`;
    }
});
