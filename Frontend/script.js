// Add this at the top of your file
const API_BASE_URL = 'http://127.0.0.1:5000'; // Replace with your actual API domain

// Fetch universities and research areas when page loads

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const [universities, researchAreas] = await Promise.all([
            fetch(`${API_BASE_URL}/api/universities`).then(res => res.json()),
            fetch(`${API_BASE_URL}/api/research-areas`).then(res => res.json())
        ]);

        const uniSelect = document.getElementById('university');
        const areaSelect = document.getElementById('research-area');
        const searchButton = document.getElementById('search-button');

        // Populate universities
        universities.forEach(uni => {
            const option = document.createElement('option');
            option.value = uni.uni_id;
            option.textContent = uni.name;
            uniSelect.appendChild(option);
        });

        // Populate research areas
        researchAreas.forEach(area => {
            const option = document.createElement('option');
            option.value = area.area;
            option.textContent = area.area;
            areaSelect.appendChild(option);
        });

        // Add event listeners for select changes
        function updateSearchButton() {
            const universityValue = uniSelect.value;
            const researchAreaValue = areaSelect.value;
            searchButton.disabled = !universityValue || !researchAreaValue;
            console.log('Button state:', searchButton.disabled, 'Uni:', universityValue, 'Area:', researchAreaValue);
        }

        uniSelect.addEventListener('change', updateSearchButton);
        areaSelect.addEventListener('change', updateSearchButton);
        
        // Add event listener for search button
        searchButton.addEventListener('click', searchScholars);

    } catch (error) {
        console.error('Error loading form data:', error);
    }
});

// Handle selections and fetch results
async function searchScholars() {
    const university = document.getElementById('university').value;
    const researchArea = document.getElementById('research-area').value;
    const professorsOnly = document.getElementById('professors-only').checked;
    const resultsDiv = document.getElementById('results');
    const totalResultsDiv = document.getElementById('total-results') || (() => {
        const div = document.createElement('div');
        div.id = 'total-results';
        resultsDiv.parentNode.insertBefore(div, resultsDiv);
        return div;
    })();

    console.log('Searching with:', { university, researchArea, professorsOnly });

    if (!university || !researchArea) {
        totalResultsDiv.innerHTML = '';
        resultsDiv.innerHTML = '<p>Please select both a university and research area.</p>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/scholars?university=${university}&area=${researchArea}`);
        const scholars = await response.json();

        // Filter for professors if checkbox is checked
        const filteredScholars = professorsOnly 
            ? scholars.filter(scholar => scholar.title.toLowerCase().includes('professor'))
            : scholars;

        totalResultsDiv.innerHTML = `<p class="results-count">Total Results: ${filteredScholars.length}</p>`;
        
        resultsDiv.innerHTML = `
            ${filteredScholars.map(scholar => `
                <div class="scholar-card">
                    <img src="${scholar.photo}" alt="${scholar.name}" onerror="this.src='default-avatar.png'">
                    <h3>${scholar.name}</h3>
                    <p>Title: ${scholar.title}</p>
                </div>
            `).join('')}`;
    } catch (error) {
        totalResultsDiv.innerHTML = '';
        console.error('Error fetching scholars:', error);
        resultsDiv.innerHTML = '<p>Error fetching results. Please try again.</p>';
    }
}