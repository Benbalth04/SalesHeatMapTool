// Select elements
const yearCheckboxes = document.querySelectorAll('#year-dropdown input[type="checkbox"]');
const stateCheckboxes = document.querySelectorAll('#state-dropdown input[type="checkbox"]');
const generateMapBtn = document.getElementById('generate-map-btn');
const mapContainer = document.getElementById('map-container');

// Function to check selections
function checkSelections() {
    const selectedStates = Array.from(stateCheckboxes).filter(checkbox => checkbox.checked).length;
    const selectedYears = Array.from(yearCheckboxes).filter(checkbox => checkbox.checked).length;

    // Enable/Disable the button
    if (selectedStates > 0 && selectedYears > 0) {
        generateMapBtn.disabled = false;
    } else {
        generateMapBtn.disabled = true;
    }
}

// Add event listeners to all checkboxes
[...yearCheckboxes, ...stateCheckboxes].forEach(checkbox => {
    checkbox.addEventListener('change', checkSelections);
});

// Generate map button event listener
generateMapBtn.addEventListener('click', async () => {
    const selectedStates = Array.from(stateCheckboxes)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);

    const selectedYears = Array.from(yearCheckboxes)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);

    const resolution = 'StateElectorate'

    const payload = {
        states: selectedStates,
        years: selectedYears,
        resolution: resolution
    };

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
        console.error('Map generation error:', error);
        mapContainer.innerHTML = `<p>An error occurred: ${error.message}</p>`;
    }
});

// Initial check to set button state on page load
checkSelections();

// Dropdown toggle functionality
document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
    toggle.addEventListener('click', () => {
        const dropdown = toggle.closest('.dropdown');
        dropdown.classList.toggle('active');
    });
});

// Close dropdowns when clicking outside
document.addEventListener('click', (event) => {
    document.querySelectorAll('.dropdown').forEach(dropdown => {
        if (!dropdown.contains(event.target)) {
            dropdown.classList.remove('active');
        }
    });
});