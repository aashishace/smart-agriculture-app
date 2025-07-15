/* Smart Irrigation Dashboard JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    loadWeatherData();
    loadIrrigationSchedule();
    
    // Auto-refresh every 10 minutes
    setInterval(loadDashboardData, 600000);
});

async function loadDashboardData() {
    try {
        const response = await fetch('/irrigation/api/dashboard-stats');
        const data = await response.json();
        
        if (data.success) {
            updateDashboardStats(data.stats);
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

async function loadWeatherData() {
    try {
        const response = await fetch('/irrigation/api/weather-recommendations');
        const data = await response.json();
        
        if (data.success) {
            updateWeatherDisplay(data.weather);
            updateGeneralRecommendation(data.recommendation);
        }
    } catch (error) {
        console.error('Error loading weather data:', error);
        document.getElementById('generalRecommendation').innerHTML = 
            '<p class="text-red-600">Weather data unavailable</p>';
    }
}

async function loadIrrigationSchedule() {
    try {
        const response = await fetch('/irrigation/api/schedule');
        const data = await response.json();
        
        if (data.success) {
            displayIrrigationSchedule(data.schedule);
        }
    } catch (error) {
        console.error('Error loading irrigation schedule:', error);
        document.getElementById('irrigationSchedule').innerHTML = 
            '<div class="text-center text-red-600 py-8">Error loading irrigation schedule</div>';
    }
}

function updateDashboardStats(stats) {
    document.getElementById('totalCrops').textContent = stats.total_crops || 0;
    document.getElementById('urgentCrops').textContent = stats.urgent_irrigation || 0;
    document.getElementById('optimalCrops').textContent = stats.optimal_status || 0;
    document.getElementById('scheduledToday').textContent = stats.scheduled_today || 0;
    
    // Update timestamp using regular JavaScript Date
    const now = new Date();
    const timeString = now.toLocaleDateString('hi-IN') + ' ' + now.toLocaleTimeString('hi-IN', {hour: '2-digit', minute: '2-digit'});
    document.getElementById('lastUpdated').textContent = timeString;
}

function updateWeatherDisplay(weather) {
    document.getElementById('currentTemp').textContent = `${weather.temperature}°C`;
    document.getElementById('currentHumidity').textContent = `${weather.humidity}%`;
    document.getElementById('rainProb').textContent = `${weather.rain_probability}%`;
}

function updateGeneralRecommendation(recommendation) {
    const element = document.getElementById('generalRecommendation');
    const bgClass = recommendation.action === 'skip' ? 'bg-red-50' : 
                   recommendation.action === 'irrigate' ? 'bg-green-50' : 'bg-yellow-50';
    const textClass = recommendation.action === 'skip' ? 'text-red-800' : 
                     recommendation.action === 'irrigate' ? 'text-green-800' : 'text-yellow-800';
    
    element.className = `p-4 rounded-lg ${bgClass}`;
    element.innerHTML = `<p class="${textClass}">${recommendation.message_hi}</p>`;
}

function displayIrrigationSchedule(schedule) {
    const container = document.getElementById('irrigationSchedule');
    
    if (!schedule || schedule.length === 0) {
        container.innerHTML = '<div class="text-center text-gray-500 py-8">कोई फसल सिंचाई के लिए तैयार नहीं है</div>';
        return;
    }
    
    container.innerHTML = schedule.map(item => createScheduleCard(item)).join('');
}

function createScheduleCard(item) {
    const priorityColors = {
        'urgent': 'border-red-500 bg-red-50',
        'high': 'border-orange-500 bg-orange-50',
        'medium': 'border-yellow-500 bg-yellow-50',
        'low': 'border-green-500 bg-green-50'
    };
    
    const priorityTextColors = {
        'urgent': 'text-red-800',
        'high': 'text-orange-800',
        'medium': 'text-yellow-800',
        'low': 'text-green-800'
    };
    
    const actionButtons = item.action === 'irrigate' ? `
        <button onclick="scheduleIrrigation(${item.crop_id}, ${item.water_amount_mm})" 
                class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition duration-300 mr-2">
            सिंचाई निर्धारित करें
        </button>
        <button onclick="showCropDetails(${item.crop_id})" 
                class="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition duration-300">
            विवरण देखें
        </button>
    ` : `
        <button onclick="showCropDetails(${item.crop_id})" 
                class="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition duration-300">
            विवरण देखें
        </button>
    `;
    
    return `
        <div class="border-l-4 ${priorityColors[item.priority]} p-4 rounded-r-lg">
            <div class="flex items-center justify-between">
                <div class="flex-1">
                    <div class="flex items-center space-x-4">
                        <h3 class="text-lg font-semibold text-gray-800">
                            ${item.crop.crop_type} - ${item.crop.variety || 'Standard'}
                        </h3>
                        <span class="px-2 py-1 rounded-full text-xs font-medium ${priorityTextColors[item.priority]} bg-white">
                            ${item.priority.toUpperCase()} प्राथमिकता
                        </span>
                    </div>
                    <div class="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                            <span class="font-medium">फार्म:</span> ${item.crop.farm_name}
                        </div>
                        <div>
                            <span class="font-medium">क्षेत्रफल:</span> ${item.crop.area_acres} एकड़
                        </div>
                        <div>
                            <span class="font-medium">अवस्था:</span> ${item.growth_stage_description}
                        </div>
                        <div>
                            <span class="font-medium">अंतिम सिंचाई:</span> ${item.days_since_irrigation} दिन पहले
                        </div>
                    </div>
                    <div class="mt-3 p-3 bg-white rounded-lg">
                        <p class="text-gray-800 font-medium">${item.message_hi}</p>
                        ${item.action === 'irrigate' ? `
                            <p class="text-sm text-gray-600 mt-1">
                                सुझाया गया पानी: <span class="font-semibold text-blue-600">${item.water_amount_mm}मिमी</span>
                            </p>
                        ` : ''}
                    </div>
                </div>
                <div class="ml-4 flex flex-col space-y-2">
                    ${actionButtons}
                </div>
            </div>
        </div>
    `;
}

async function scheduleIrrigation(cropId, waterAmount) {
    if (!confirm(`क्या आप ${waterAmount}मिमी पानी की सिंचाई निर्धारित करना चाहते हैं?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/crops/api/${cropId}/schedule-irrigation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                water_amount_mm: waterAmount
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('सफलता!', 'सिंचाई निर्धारित की गई! SMS भेजा गया।', 'success');
            loadIrrigationSchedule(); // Refresh the schedule
            loadDashboardData(); // Refresh stats
        } else {
            showNotification('त्रुटि!', data.error || 'कुछ गलत हुआ', 'error');
        }
    } catch (error) {
        console.error('Error scheduling irrigation:', error);
        showNotification('त्रुटि!', 'नेटवर्क त्रुटि। कृपया पुनः प्रयास करें।', 'error');
    }
}

async function bulkScheduleIrrigation() {
    if (!confirm('क्या आप सभी जरूरी फसलों के लिए सिंचाई निर्धारित करना चाहते हैं?')) {
        return;
    }
    
    try {
        const response = await fetch('/irrigation/api/schedule-all-urgent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('सफलता!', `${data.scheduled_count} फसलों के लिए सिंचाई निर्धारित की गई!`, 'success');
            loadIrrigationSchedule();
            loadDashboardData();
        } else {
            showNotification('त्रुटि!', data.error || 'कुछ गलत हुआ', 'error');
        }
    } catch (error) {
        console.error('Error bulk scheduling:', error);
        showNotification('त्रुटि!', 'नेटवर्क त्रुटि। कृपया पुनः प्रयास करें।', 'error');
    }
}

async function generateAllRecommendations() {
    try {
        showNotification('जानकारी', 'सभी सिफारिशें अपडेट की जा रही हैं...', 'info');
        
        const response = await fetch('/irrigation/api/refresh-all-recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('सफलता!', 'सभी सिफारिशें अपडेट की गईं!', 'success');
            loadIrrigationSchedule();
            loadDashboardData();
        } else {
            showNotification('त्रुटि!', data.error || 'कुछ गलत हुआ', 'error');
        }
    } catch (error) {
        console.error('Error refreshing recommendations:', error);
        showNotification('त्रुटि!', 'नेटवर्क त्रुटि। कृपया पुनः प्रयास करें।', 'error');
    }
}

function showCropDetails(cropId) {
    window.location.href = `/crops/${cropId}`;
}

function showNotification(title, message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;
    
    const bgColor = type === 'success' ? 'bg-green-500' : 
                   type === 'error' ? 'bg-red-500' : 
                   type === 'info' ? 'bg-blue-500' : 'bg-gray-500';
    
    notification.classList.add(bgColor, 'text-white');
    
    notification.innerHTML = `
        <div class="flex items-center space-x-3">
            <div>
                <h4 class="font-semibold">${title}</h4>
                <p class="text-sm">${message}</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="text-white hover:text-gray-200">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}
