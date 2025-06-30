# Screenshot Generation Instructions

## To Generate Screenshots for Project Report

### Prerequisites
1. Ensure the Flask application is running: `python run.py`
2. Login with demo credentials: 9876543210 / password123
3. Have a web browser with developer tools for mobile simulation

### Screenshot Capture Process

#### Method 1: Browser Screenshots
1. Open each URL in your browser
2. Use F12 developer tools for mobile views
3. Take full-page screenshots using browser extensions like:
   - Full Page Screen Capture (Chrome)
   - Firefox Screenshot (Firefox)
   - Awesome Screenshot (Multi-browser)

#### Method 2: Programmatic Screenshots (Recommended)
Install selenium for automated screenshot capture:

```bash
pip install selenium webdriver-manager
```

Create screenshot automation script:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

def capture_screenshots():
    # Setup Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    screenshots = [
        ('http://127.0.0.1:5000/dashboard', '01_dashboard_overview.png'),
        ('http://127.0.0.1:5000/farms', '02_farm_management.png'),
        ('http://127.0.0.1:5000/crops', '03_crop_management.png'),
        ('http://127.0.0.1:5000/ai/disease-scanner', '04_disease_detection.png'),
        # Add more URLs as needed
    ]
    
    for url, filename in screenshots:
        driver.get(url)
        time.sleep(3)  # Wait for page to load
        driver.save_screenshot(f'screenshots/{filename}')
        print(f'Captured: {filename}')
    
    driver.quit()

if __name__ == '__main__':
    capture_screenshots()
```

### Manual Screenshot Guidelines

1. **Dashboard Overview** (01_dashboard_overview.png)
   - Navigate to http://127.0.0.1:5000/dashboard
   - Wait for all charts to load completely
   - Ensure today's tasks are visible
   - Capture full page including header and footer

2. **Farm Management** (02_farm_management.png)
   - Navigate to http://127.0.0.1:5000/farms
   - Show the farm listing with all 3 farms
   - Include statistics and map if visible

3. **Crop Management** (03_crop_management.png)
   - Navigate to http://127.0.0.1:5000/crops
   - Show both active and harvested crops
   - Include crop details and growth stages

4. **Disease Detection** (04_disease_detection.png)
   - Navigate to http://127.0.0.1:5000/ai/disease-scanner
   - Show the upload interface
   - If possible, include a detection result

5. **Mobile View** (07_mobile_interface.png)
   - Use Chrome DevTools (F12)
   - Select iPhone/Android simulation
   - Capture dashboard in mobile view

### Technical Diagrams

For technical diagrams (architecture, database schema), use tools like:
- **Draw.io** (free online diagram tool)
- **Lucidchart** (professional diagramming)
- **PlantUML** (code-based diagrams)
- **Mermaid** (markdown-based diagrams)

### File Organization

```
screenshots/
├── 01_dashboard_overview.png
├── 02_farm_management.png
├── 03_crop_management.png
├── 04_disease_detection.png
├── 05_activity_management.png
├── 06_analytics_dashboard.png
├── 07_mobile_interface.png
├── 08_login_system.png
├── 09_crop_analytics.png
├── 10_system_architecture.png
├── 11_api_testing.png
├── 12_performance_metrics.png
├── 13_user_testing.png
├── 14_security_implementation.png
├── 15_project_evolution.png
├── 16_tech_integration.png
├── 17_impact_analysis.png
└── 18_deployment_architecture.png
```

### Quality Checklist

- [ ] All screenshots are high resolution (minimum 1200px width)
- [ ] Charts and data are clearly visible
- [ ] Hindi text is readable
- [ ] All key features are highlighted
- [ ] Mobile screenshots show responsive design
- [ ] Technical diagrams are professionally formatted
- [ ] File sizes are optimized for report inclusion

### After Capturing Screenshots

1. Review each screenshot for clarity and completeness
2. Optimize file sizes if needed (use tools like TinyPNG)
3. Ensure all referenced features are visible
4. Test that all image links work in the report
5. Add any necessary annotations or callouts

The project report now includes comprehensive screenshot placeholders and detailed descriptions that demonstrate the full functionality of the Smart Agriculture App.
