document.addEventListener('DOMContentLoaded', function() {
    const diseaseForm = document.getElementById('diseaseForm');
    if (!diseaseForm) return;

    // --- DOM Elements ---
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const cropSelect = document.getElementById('crop_id');
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = document.getElementById('btnText');
    const loadingText = document.getElementById('loadingText');
    
    const identifyBtn = document.getElementById('identifyBtn');
    const identifyBtnText = document.getElementById('identifyBtnText');
    const identifyingText = document.getElementById('identifyingText');

    const resultsSection = document.getElementById('resultsSection');
    const newScanBtn = document.getElementById('newScanBtn');

    // --- Initial State Check ---
    if (analyzeBtn.dataset.disabled === 'true') {
        const scannerContainer = document.querySelector('.max-w-4xl');
        if(scannerContainer) {
            scannerContainer.innerHTML = `
                <div class="bg-yellow-50 border-l-4 border-yellow-400 text-yellow-700 p-4" role="alert">
                    <p class="font-bold">${diseaseForm.dataset.unavailableTitle}</p>
                    <p>${diseaseForm.dataset.unavailableMessage}</p>
                </div>
            `;
        }
        return;
    }

    // --- Event Listeners ---
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => handleFileSelection(e.target.files[0]));
    cropSelect.addEventListener('change', checkFormValidity);
    
    // Drag and Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.add('border-green-500'), false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('border-green-500'), false);
    });
    uploadArea.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelection(files[0]);
        }
    });

    // --- Button Clicks ---
    diseaseForm.addEventListener('submit', handleDiseaseAnalysis);
    identifyBtn.addEventListener('click', handlePlantIdentification);

    // --- Functions ---
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleFileSelection(file) {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                uploadPlaceholder.classList.add('hidden');
                imagePreview.classList.remove('hidden');
                checkFormValidity();
            };
            reader.readAsDataURL(file);
        }
    }

    function checkFormValidity() {
        const fileSelected = fileInput.files.length > 0;
        analyzeBtn.disabled = !fileSelected;
        identifyBtn.disabled = !fileSelected;
    }

    function handleDiseaseAnalysis(e) {
        e.preventDefault();
        const formData = new FormData(diseaseForm);
        
        toggleLoading(true, 'disease');
        
        fetch(diseaseForm.action, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showDiseaseResults(data.result);
            } else {
                showError(data.error || diseaseForm.dataset.errorAnalysis);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError(diseaseForm.dataset.errorNetwork);
        })
        .finally(() => toggleLoading(false, 'disease'));
    }

    function handlePlantIdentification() {
        const formData = new FormData();
        if (fileInput.files.length === 0) {
            showError(diseaseForm.dataset.errorNoImage);
            return;
        }
        formData.append('image', fileInput.files[0]);

        toggleLoading(true, 'identify');

        fetch('/api/plant-identify', {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showIdentificationResults(data);
            } else {
                showError(data.error || 'Could not identify the plant.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError(diseaseForm.dataset.errorNetwork);
        })
        .finally(() => toggleLoading(false, 'identify'));
    }

    function toggleLoading(isLoading, type) {
        if (type === 'disease') {
            btnText.classList.toggle('hidden', isLoading);
            loadingText.classList.toggle('hidden', !isLoading);
            analyzeBtn.disabled = isLoading;
            identifyBtn.disabled = isLoading;
        } else if (type === 'identify') {
            identifyBtnText.classList.toggle('hidden', isLoading);
            identifyingText.classList.toggle('hidden', !isLoading);
            analyzeBtn.disabled = isLoading;
            identifyBtn.disabled = isLoading;
        }
    }

    function showDiseaseResults(result) {
        const isHealthy = result.is_healthy;
        const confidence = result.confidence.toFixed(1);
        const statusColor = isHealthy ? 'green' : 'red';
        const statusIcon = isHealthy ? '✅' : '⚠️';
        
        let content = `
            <div class="border border-gray-200 rounded-lg p-6">
                <div class="flex items-start space-x-4">
                    <div class="text-4xl">${statusIcon}</div>
                    <div class="flex-1">
                        <h3 class="text-xl font-semibold text-${statusColor}-600 mb-2">${isHealthy ? resultsSection.dataset.healthyTitle : resultsSection.dataset.diseaseTitle}</h3>
                        <p class="text-gray-700 mb-4">
                            ${isHealthy ? resultsSection.dataset.healthyMessage : resultsSection.dataset.diseaseMessage.replace('{disease}', `<strong>${result.disease}</strong> (${result.disease_en})`)}
                        </p>
                        <div class="mb-4">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-sm font-medium">${resultsSection.dataset.confidenceLabel}</span>
                                <span class="text-sm font-bold">${confidence}%</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2"><div class="bg-${statusColor}-600 h-2 rounded-full" style="width: ${confidence}%"></div></div>
                        </div>
                        ${!isHealthy && result.treatment ? `<div class="bg-${statusColor}-50 border border-${statusColor}-200 rounded-lg p-4 mb-4"><h4 class="font-semibold text-${statusColor}-800 mb-2">${resultsSection.dataset.treatmentTitle}</h4><div class="text-sm text-${statusColor}-700">${formatTreatment(result.treatment)}</div></div>` : ''}
                    </div>
                </div>
            </div>
        `;
        displayResults(content);
    }

    function showIdentificationResults(result) {
        const confidence = result.confidence.toFixed(1);
        let content = `
            <div class="border border-gray-200 rounded-lg p-6">
                <div class="flex items-start space-x-4">
                    <div class="text-4xl">🌿</div>
                    <div class="flex-1">
                        <h3 class="text-xl font-semibold text-green-600 mb-2">Plant Identified</h3>
                        <p class="text-gray-700 mb-4">
                            We've identified this plant as <strong>${result.plant_name}</strong>.
                        </p>
                        <div class="mb-4">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-sm font-medium">Confidence Level</span>
                                <span class="text-sm font-bold">${confidence}%</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2"><div class="bg-green-600 h-2 rounded-full" style="width: ${confidence}%"></div></div>
                        </div>
                        <div class="text-sm space-y-2">
                            <p><strong>Common Names:</strong> ${result.common_names.join(', ') || 'N/A'}</p>
                            <p><strong>Family:</strong> ${result.family}</p>
                            <p><strong>Genus:</strong> ${result.genus}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        displayResults(content);
    }

    function displayResults(innerHTML) {
        const resultsContent = document.getElementById('resultsContent');
        resultsContent.innerHTML = innerHTML;
        resultsSection.classList.remove('hidden');
        document.getElementById('uploadSection').classList.add('hidden');
    }

    function showError(message) {
        let errorHtml = `
            <div class="border border-red-200 rounded-lg p-6 bg-red-50">
                <div class="flex items-start space-x-4">
                    <div class="text-4xl">❌</div>
                    <div class="flex-1">
                        <h3 class="text-xl font-semibold text-red-600 mb-2">${resultsSection.dataset.errorTitle}</h3>
                        <p class="text-red-700">${message}</p>
                        <p class="text-sm text-red-600 mt-2">${resultsSection.dataset.errorMessage}</p>
                    </div>
                </div>
            </div>
        `;
        displayResults(errorHtml);
    }

    function formatTreatment(treatment) {
        if (typeof treatment === 'string') return `<p>${treatment}</p>`;
        let html = '';
        if (treatment.urgency) html += `<div class="mb-3 p-2 bg-red-100 border border-red-300 rounded text-red-800 font-medium">${treatment.urgency}</div>`;
        if (treatment.immediate) html += `<div class="mb-2"><strong>${resultsSection.dataset.immediateActionLabel}:</strong> ${treatment.immediate}</div>`;
        if (treatment.chemical) html += `<div class="mb-2"><strong>${resultsSection.dataset.chemicalTreatmentLabel}:</strong> ${treatment.chemical}</div>`;
        if (treatment.organic) html += `<div class="mb-2"><strong>${resultsSection.dataset.organicTreatmentLabel}:</strong> ${treatment.organic}</div>`;
        if (treatment.frequency) html += `<div class="mb-2"><strong>${resultsSection.dataset.frequencyLabel}:</strong> ${treatment.frequency}</div>`;
        if (treatment.precautions) html += `<div class="mb-2"><strong>${resultsSection.dataset.precautionsLabel}:</strong> ${treatment.precautions}</div>`;
        return html;
    }

    newScanBtn.addEventListener('click', () => {
        fileInput.value = '';
        uploadPlaceholder.classList.remove('hidden');
        imagePreview.classList.add('hidden');
        resultsSection.classList.add('hidden');
        document.getElementById('uploadSection').classList.remove('hidden');
        analyzeBtn.disabled = true;
        identifyBtn.disabled = true;
        cropSelect.value = '';
    });
});
