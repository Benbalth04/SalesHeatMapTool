const countries = [
    "Australia"
];

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Select2 and Flatpickr
    const countryDropdown = document.getElementById('country-select');
        countries.forEach(country => {
            const option = document.createElement('option');
            option.value = country;
            option.textContent = country;
            countryDropdown.appendChild(option);
    });

    $('#resolution-select, #time-resolution-select').select2();

    flatpickr('#date-range', {
        mode: 'range',
        dateFormat: 'Y-m-d',
    });

    // Enable/disable Generate Map button
    const inputs = ['#country-select', '#resolution-select', '#time-resolution-select', '#date-range'];
    const generateMapBtn = document.getElementById('generate-map-btn');

    function checkInputs() {
        const allFilled = inputs.every((selector) => $(selector).val() && $(selector).val().length > 0);
        generateMapBtn.disabled = !allFilled;
    }

    inputs.forEach((selector) => {
        $(selector).on('change', checkInputs);
    });

    // Generate Map Button Click
    generateMapBtn.addEventListener('click', () => {
        alert('Map Generated!');
        $('#reset-btn').show();
        generateMapBtn.disabled = true;
    });

    // Reset Button Click
    document.getElementById('reset-btn').addEventListener('click', () => {
        $('select').val(null).trigger('change');
        flatpickr('#date-range').clear();
        $('#reset-btn').hide();
        generateMapBtn.disabled = true;
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const timeResolutionSelect = document.getElementById("time-resolution-select");
    const dateRangeInput = document.getElementById("date-range");

    if (!timeResolutionSelect || !dateRangeInput) {
        console.error("Required elements not found in the DOM.");
        return;
    }
    console.log(`Selected resolution: ${timeResolutionSelect}`);


    // Initialize Flatpickr
    let calendar = flatpickr(dateRangeInput, {
        enableTime: false, 
        dateFormat: "Y-m-d", 
    });

    // Update the calendar when time resolution changes
    timeResolutionSelect.addEventListener("change", (event) => {
        console.log(`Selected resolution: ${timeResolutionSelect}`);

        const resolution = event.target.value;

        // Destroy the current calendar instance
        if (calendar) {
            calendar.destroy();
        }

        // Re-initialize Flatpickr based on selected resolution
        switch (resolution) {
            case "Years":
                calendar = flatpickr(dateRangeInput, {
                    dateFormat: "Y",
                    mode: "single", // Single year selection
                    disableMobile: true,
                });
                break;

            case "Quarters":
                calendar = flatpickr(dateRangeInput, {
                    mode: "range", // Select a range of dates to define a quarter
                    dateFormat: "Y [Q]Q",
                    onClose: (selectedDates) => {
                        if (selectedDates.length > 0) {
                            const startMonth = selectedDates[0].getMonth();
                            const quarter = Math.ceil((startMonth + 1) / 3);
                            const year = selectedDates[0].getFullYear();
                            dateRangeInput.value = `${year} Q${quarter}`;
                        }
                    },
                });
                break;

            case "Months":
                calendar = flatpickr(dateRangeInput, {
                    dateFormat: "F Y",
                    mode: "single", // Single month selection
                    disableMobile: true,
                });
                break;

            default:
                calendar = flatpickr(dateRangeInput, {
                    enableTime: false,
                    dateFormat: "Y-m-d",
                });
        }
    });
});

// Select elements
// document.addEventListener('DOMContentLoaded', () => {
//     const yearCheckboxes = document.querySelectorAll('#year-dropdown input[type="checkbox"]');
//     const stateCheckboxes = document.querySelectorAll('#state-dropdown input[type="checkbox"]');
//     const resolutionDropdown = document.getElementById('resolution-dropdown');
//     const generateMapBtn = document.getElementById('generate-map-btn');
//     const loadingOverlay = document.getElementById("loading-overlay");
//     const dropdownsContainer = document.getElementById("dropdowns-container");
//     const resolutionContainer = document.getElementById("resolution-container");

//     // Function to check selections
//     function checkSelections() {
//         const selectedStates = Array.from(stateCheckboxes).filter(checkbox => checkbox.checked).length;
//         const selectedYears = Array.from(yearCheckboxes).filter(checkbox => checkbox.checked).length;
//         const resolutionSelected = resolutionDropdown.value !== '';
//         resolution = resolutionDropdown.value

//         // Enable/Disable the button
//         if (selectedStates > 0 && selectedYears > 0 && resolutionSelected) {
//             generateMapBtn.disabled = false;
//         } else {
//             generateMapBtn.disabled = true;
//         }
//     }

//     // Add event listeners to all checkboxes
//     yearCheckboxes.forEach(checkbox => checkbox.addEventListener('change', checkSelections));
//     stateCheckboxes.forEach(checkbox => checkbox.addEventListener('change', checkSelections));
//     resolutionDropdown.addEventListener('change', checkSelections);

//     checkSelections();

//     // Generate map button event listener
//     generateMapBtn.addEventListener('click', async () => {

//         if (generateMapBtn.classList.contains('reset')) {
//             resetPage();
//             return;
//         }

//         const selectedStates = Array.from(stateCheckboxes)
//             .filter(checkbox => checkbox.checked)
//             .map(checkbox => checkbox.value);

//         const selectedYears = Array.from(yearCheckboxes)
//             .filter(checkbox => checkbox.checked)
//             .map(checkbox => checkbox.value);

//         const resolution = resolutionDropdown.value;

//         const payload = {
//             states: selectedStates,
//             years: selectedYears,
//             resolution: resolution
//         };

//         showLoading()

//         try {
//             const response = await fetch('/api/generate-map', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify(payload),
//             });

//             if (!response.ok) {
//                 throw new Error(`HTTP error! status: ${response.status}`);
//             }

//             const data = await response.json();
//             const htmlFilePath = data.htmlFilePath;

//             // Create the iframe to load the generated map
//             const iframe = document.createElement('iframe');
//             iframe.src = htmlFilePath;
//             iframe.width = "100%";
//             iframe.height = "100%";

//             // Clear the previous content (if any) and append the iframe to the container
//             mapContainer.innerHTML = '';
//             mapContainer.appendChild(iframe);

//             // Hide dropdowns and change button to reset
//             dropdownsContainer.classList.add('hidden');
//             resolutionContainer.classList.add('hidden')

//             generateMapBtn.classList.add('reset');
//             generateMapBtn.textContent = "Reset";

//         } catch (error) {
//             hideLoading()
//             console.error('Map generation error:', error);
//             mapContainer.innerHTML = `<p>An error occurred: ${error.message}</p>`;
//         }
//     });

//     async function resetPage() {
//         // Uncheck all checkboxes
//         yearCheckboxes.forEach(checkbox => checkbox.checked = false);
//         stateCheckboxes.forEach(checkbox => checkbox.checked = false);

//         resolutionDropdown.value = '';
//         mapContainer.innerHTML = '';
//         dropdownsContainer.classList.remove('hidden');
//         resolutionContainer.classList.remove('hidden')


//         // Reset button text and state
//         generateMapBtn.classList.remove('reset');
//         generateMapBtn.textContent = "Generate Map";
//         generateMapBtn.disabled = true; // Disable until selections are made

//         // Call an API or function to delete the map files from the server
//         try {
//             const response = await fetch('/api/reset-maps', {
//                 method: 'DELETE',
//             });

//             if (!response.ok) {
//                 throw new Error(`HTTP error! status: ${response.status}`);
//             }
//             const data = await response.json();
//             console.log('File deleted successfully:', data.message);
            
//         } catch (error) {
//             console.error('Error resetting maps:', error);
//         }
//     };


//     // Dropdown toggle functionality
//     document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
//         toggle.addEventListener('click', () => {
//             const dropdown = toggle.closest('.dropdown');
//             dropdown.classList.toggle('active');
//         });
//     });

//     // Close dropdowns when clicking outside
//     document.addEventListener('click', (event) => {
//         document.querySelectorAll('.dropdown').forEach(dropdown => {
//             if (!dropdown.contains(event.target)) {
//                 dropdown.classList.remove('active');
//             }
//         });
//     });

//     // Show loading overlay
//     function showLoading() {
//         loadingOverlay.style.visibility = "visible";
//     }

//     // Hide loading overlay
//     function hideLoading() {
//         loadingOverlay.style.visibility = "hidden";
//     }
// });