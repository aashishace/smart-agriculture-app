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
        const confidence = parseFloat(result.confidence || 0).toFixed(1);
        const statusColor = isHealthy ? 'green' : getStatusColor(result.confidence_level);
        const statusIcon = isHealthy ? '✅' : getSeverityIcon(result.severity);
        const reliabilityMessage = result.reliability_message || '';
        
        let content = `
            <div class="border border-gray-200 rounded-lg p-6">
                <div class="flex items-start space-x-4">
                    <div class="text-4xl">${statusIcon}</div>
                    <div class="flex-1">
                        <h3 class="text-xl font-semibold text-${statusColor}-600 mb-2">
                            ${isHealthy ? resultsSection.dataset.healthyTitle : resultsSection.dataset.diseaseTitle}
                        </h3>
                        <p class="text-gray-700 mb-4">
                            ${isHealthy ? 
                                resultsSection.dataset.healthyMessage : 
                                resultsSection.dataset.diseaseMessage.replace('{disease}', `<strong>${result.disease}</strong>`)}
                        </p>
                        
                        <!-- Confidence and Reliability -->
                        <div class="mb-4">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-sm font-medium">${resultsSection.dataset.confidenceLabel}</span>
                                <span class="text-sm font-bold">${confidence}% (${result.confidence_level || 'unknown'})</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="bg-${statusColor}-600 h-2 rounded-full" style="width: ${confidence}%"></div>
                            </div>
                            ${reliabilityMessage ? `<p class="text-sm text-gray-600 mt-1">${reliabilityMessage}</p>` : ''}
                        </div>

                        <!-- Crop and Disease Information -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div class="bg-blue-50 p-3 rounded">
                                <h4 class="font-semibold text-blue-800">Detected Crop</h4>
                                <p class="text-blue-700">${result.crop_type || 'Unknown'}</p>
                            </div>
                            <div class="bg-${statusColor}-50 p-3 rounded">
                                <h4 class="font-semibold text-${statusColor}-800">Disease Status</h4>
                                <p class="text-${statusColor}-700">${result.disease}</p>
                            </div>
                        </div>

                        <!-- Treatment Information -->
                        ${!isHealthy && result.treatment ? formatTreatmentSection(result.treatment, statusColor) : ''}
                        
                        <!-- Prevention Recommendations -->
                        ${result.recommendations && result.recommendations.length > 0 ? formatRecommendations(result.recommendations) : ''}
                        
                        <!-- Analysis Details -->
                        ${result.analysis_details ? formatAnalysisDetails(result.analysis_details) : ''}
                    </div>
                </div>
            </div>
        `;
        displayResults(content);
    }

    function getStatusColor(confidenceLevel) {
        switch(confidenceLevel) {
            case 'high': return 'green';
            case 'medium': return 'yellow';
            case 'low': return 'orange';
            case 'very_low': return 'red';
            case 'error': return 'red';
            default: return 'gray';
        }
    }

    function getSeverityIcon(severity) {
        switch(severity) {
            case 'high': return '🚨';
            case 'medium': return '⚠️';
            case 'low': return '🔍';
            case 'none': return '✅';
            default: return '❓';
        }
    }

    function formatTreatmentSection(treatment, statusColor) {
        const urgencyColors = {
            'very_high': 'red',
            'high': 'red',
            'medium': 'yellow',
            'low': 'blue'
        };
        
        const urgencyColor = urgencyColors[treatment.urgency] || 'gray';
        
        return `
            <div class="bg-${statusColor}-50 border border-${statusColor}-200 rounded-lg p-4 mb-4">
                <h4 class="font-semibold text-${statusColor}-800 mb-3">
                    ${resultsSection.dataset.treatmentTitle}
                    ${treatment.urgency ? `<span class="ml-2 px-2 py-1 bg-${urgencyColor}-100 text-${urgencyColor}-800 text-xs rounded">${treatment.urgency.replace('_', ' ').toUpperCase()}</span>` : ''}
                </h4>
                <div class="text-sm text-${statusColor}-700 space-y-3">
                    ${treatment.immediate_action ? `<div><strong>🚀 Immediate Action:</strong> ${treatment.immediate_action}</div>` : ''}
                    ${treatment.organic_treatment ? `<div><strong>🌱 Organic Treatment:</strong> ${treatment.organic_treatment}</div>` : ''}
                    ${treatment.chemical_treatment ? `<div><strong>🧪 Chemical Treatment:</strong> ${treatment.chemical_treatment}</div>` : ''}
                    ${treatment.prevention ? `<div><strong>🛡️ Prevention:</strong> ${treatment.prevention}</div>` : ''}
                    ${treatment.estimated_cost ? `<div><strong>💰 Estimated Cost:</strong> ${treatment.estimated_cost}</div>` : ''}
                    ${treatment.treatment_duration ? `<div><strong>⏱️ Duration:</strong> ${treatment.treatment_duration}</div>` : ''}
                </div>
            </div>
        `;
    }

    function formatRecommendations(recommendations) {
        const recommendationsByCategory = {};
        recommendations.forEach(rec => {
            if (!recommendationsByCategory[rec.category]) {
                recommendationsByCategory[rec.category] = [];
            }
            recommendationsByCategory[rec.category].push(rec);
        });

        let html = `
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <h4 class="font-semibold text-blue-800 mb-3">📋 Prevention Recommendations</h4>
                <div class="space-y-3">
        `;

        Object.entries(recommendationsByCategory).forEach(([category, recs]) => {
            html += `<div class="bg-white p-3 rounded border-l-4 border-blue-400">`;
            html += `<h5 class="font-medium text-blue-700 mb-2">${category}</h5>`;
            html += `<ul class="space-y-1">`;
            
            recs.forEach(rec => {
                const priorityColor = rec.priority === 'high' ? 'red' : rec.priority === 'medium' ? 'yellow' : 'green';
                html += `
                    <li class="flex items-start text-sm">
                        <span class="w-2 h-2 bg-${priorityColor}-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                        <span class="flex-1">${rec.recommendation}</span>
                        ${rec.frequency ? `<span class="text-xs text-gray-500 ml-2">(${rec.frequency})</span>` : ''}
                    </li>
                `;
            });
            
            html += `</ul></div>`;
        });

        html += `</div></div>`;
        return html;
    }

    function formatAnalysisDetails(details) {
        return `
            <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 class="font-semibold text-gray-800 mb-3">🔬 Analysis Details</h4>
                <div class="text-sm text-gray-700 space-y-2">
                    ${details.model_prediction ? `<div><strong>Model Prediction:</strong> ${details.model_prediction}</div>` : ''}
                    ${details.model_confidence ? `<div><strong>Raw Confidence:</strong> ${(details.model_confidence * 100).toFixed(2)}%</div>` : ''}
                    ${details.model_version ? `<div><strong>Model Version:</strong> ${details.model_version}</div>` : ''}
                    ${details.image_processed ? `<div><strong>Status:</strong> ✅ Image processed successfully</div>` : ''}
                    ${details.all_predictions && details.all_predictions.length > 1 ? formatAlternativePredictions(details.all_predictions) : ''}
                    ${details.error ? `<div class="text-red-600"><strong>Error:</strong> ${details.error}</div>` : ''}
                </div>
            </div>
        `;
    }

    function formatAlternativePredictions(predictions) {
        if (predictions.length <= 1) return '';
        
        let html = `<div><strong>Alternative Predictions:</strong><ul class="ml-4 mt-1">`;
        predictions.slice(1, 3).forEach((pred, index) => {
            html += `<li>${index + 2}. ${pred.label.replace(/_/g, ' ')} (${(pred.score * 100).toFixed(1)}%)</li>`;
        });
        html += `</ul></div>`;
        return html;
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
        if (treatment.immediate_action) html += `<div class="mb-2"><strong>${resultsSection.dataset.immediateActionLabel || 'Immediate Action'}:</strong> ${treatment.immediate_action}</div>`;
        if (treatment.chemical_treatment) html += `<div class="mb-2"><strong>${resultsSection.dataset.chemicalTreatmentLabel || 'Chemical Treatment'}:</strong> ${treatment.chemical_treatment}</div>`;
        if (treatment.organic_treatment) html += `<div class="mb-2"><strong>${resultsSection.dataset.organicTreatmentLabel || 'Organic Treatment'}:</strong> ${treatment.organic_treatment}</div>`;
        if (treatment.frequency) html += `<div class="mb-2"><strong>${resultsSection.dataset.frequencyLabel || 'Frequency'}:</strong> ${treatment.frequency}</div>`;
        if (treatment.prevention) html += `<div class="mb-2"><strong>${resultsSection.dataset.precautionsLabel || 'Prevention'}:</strong> ${treatment.prevention}</div>`;
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
