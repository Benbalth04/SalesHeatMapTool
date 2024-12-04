// Select elements
document.addEventListener('DOMContentLoaded', () => {
    const yearCheckboxes = document.querySelectorAll('#year-dropdown input[type="checkbox"]');
    const stateCheckboxes = document.querySelectorAll('#state-dropdown input[type="checkbox"]');
    const resolutionDropdown = document.getElementById('resolution-dropdown');
    const generateMapBtn = document.getElementById('generate-map-btn');
    const loadingOverlay = document.getElementById("loading-overlay");
    const dropdownsContainer = document.getElementById("dropdowns-container");
    const resolutionContainer = document.getElementById("resolution-container");


    if (!yearCheckboxes.length || !stateCheckboxes.length || !resolutionDropdown || !generateMapBtn) {
        console.error("Some elements are missing in the DOM!");
        return;
    }
   
    // Function to check selections
    function checkSelections() {
        const selectedStates = Array.from(stateCheckboxes).filter(checkbox => checkbox.checked).length;
        const selectedYears = Array.from(yearCheckboxes).filter(checkbox => checkbox.checked).length;
        const resolutionSelected = resolutionDropdown.value !== '';
        resolution = resolutionDropdown.value

        // Enable/Disable the button
        if (selectedStates > 0 && selectedYears > 0 && resolutionSelected) {
            generateMapBtn.disabled = false;
        } else {
            generateMapBtn.disabled = true;
        }
    }

    // Add event listeners to all checkboxes
    yearCheckboxes.forEach(checkbox => checkbox.addEventListener('change', checkSelections));
    stateCheckboxes.forEach(checkbox => checkbox.addEventListener('change', checkSelections));
    resolutionDropdown.addEventListener('change', checkSelections);

    checkSelections();

    // Generate map button event listener
    generateMapBtn.addEventListener('click', async () => {

        if (generateMapBtn.classList.contains('reset')) {
            resetPage();
            return;
        }

        const selectedStates = Array.from(stateCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        const selectedYears = Array.from(yearCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        const resolution = resolutionDropdown.value;

        const payload = {
            states: selectedStates,
            years: selectedYears,
            resolution: resolution
        };

        showLoading()

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

            // Hide dropdowns and change button to reset
            dropdownsContainer.classList.add('hidden');
            resolutionContainer.classList.add('hidden')

            generateMapBtn.classList.add('reset');
            generateMapBtn.textContent = "Reset";

        } catch (error) {
            hideLoading()
            console.error('Map generation error:', error);
            mapContainer.innerHTML = `<p>An error occurred: ${error.message}</p>`;
        }
    });

    async function resetPage() {
        // Uncheck all checkboxes
        yearCheckboxes.forEach(checkbox => checkbox.checked = false);
        stateCheckboxes.forEach(checkbox => checkbox.checked = false);

        resolutionDropdown.value = '';
        mapContainer.innerHTML = '';
        dropdownsContainer.classList.remove('hidden');
        resolutionContainer.classList.remove('hidden')


        // Reset button text and state
        generateMapBtn.classList.remove('reset');
        generateMapBtn.textContent = "Generate Map";
        generateMapBtn.disabled = true; // Disable until selections are made

        // Call an API or function to delete the map files from the server
        try {
            const response = await fetch('/api/reset-maps', {
                method: 'DELETE',
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('File deleted successfully:', data.message);
            
        } catch (error) {
            console.error('Error resetting maps:', error);
        }
    };


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

    // Show loading overlay
    function showLoading() {
        loadingOverlay.style.visibility = "visible";
    }

    // Hide loading overlay
    function hideLoading() {
        loadingOverlay.style.visibility = "hidden";
    }
});
