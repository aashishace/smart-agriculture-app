# Disease Detection and Plant Identification Analysis

This document provides a detailed analysis of the disease detection and plant identification features in the Smart Crop Care Assistant application.

## Disease Detection

The disease detection feature allows users to upload an image of a plant and get an AI-powered diagnosis of any diseases.

### Implementation Details

The core logic for disease detection is located in `app/routes/ai.py`. The process is as follows:

1.  **Model Loading:** The application uses a pre-trained image classification model from Hugging Face: `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`. The model is loaded using the `pipeline` function from the `transformers` library.

2.  **Image Upload:** The user uploads an image through the `/ai/disease-scanner` page, which sends a POST request to the `/ai/detect-disease` endpoint.

3.  **Image Processing:** The `detect_disease` function in `app/routes/ai.py` handles the image upload. It saves the image to a temporary file and then calls the `process_disease_detection` function.

4.  **Disease Classification:** The `process_disease_detection` function uses the loaded Hugging Face pipeline to classify the image. The pipeline returns a list of predictions, with the top prediction being the most likely disease.

5.  **Result Parsing:** The application parses the prediction to extract the disease name and confidence score. It also determines if the plant is healthy based on the prediction label.

6.  **Treatment Information:** The `get_treatment_details` function retrieves treatment information from the `DiseaseInfo` table in the database based on the predicted disease name.

7.  **Database Storage:** The detection results, including the predicted disease, confidence score, and suggested treatment, are stored in the `DiseaseDetection` table.

8.  **Response:** The detection results are returned to the user as a JSON object.

### Database Schema

The following database models are used for the disease detection feature:

*   **`DiseaseDetection` (`app/models/crop.py`):** Stores the results of each disease detection, including the crop ID, image path, predicted disease, confidence score, and suggested treatment.
*   **`DiseaseInfo` (`app/models/crop_data.py`):** Stores information about different diseases, including their names, severity, and treatment recommendations.

## Plant Identification

The plant identification feature allows users to upload an image of a plant and identify it using the PlantNet API.

### Implementation Details

The logic for plant identification is located in `app/routes/api.py`. The process is as follows:

1.  **API Key:** The application uses an API key from the `PLANTNET_API_KEY` environment variable to authenticate with the PlantNet API.

2.  **Image Upload:** The user uploads an image, which sends a POST request to the `/api/plant-identify` endpoint.

3.  **API Call:** The `identify_plant` function calls the `call_plantnet_api` function, which sends a POST request to the PlantNet API (`https://my-api.plantnet.org/v2/identify/all`) with the image.

4.  **API Response:** The PlantNet API returns a JSON response containing the identified plant's scientific name, common names, and confidence score.

5.  **Response:** The processed results are returned to the user as a JSON object.
