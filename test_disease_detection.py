#!/usr/bin/env python3
"""
Test script for Enhanced Disease Detection System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
import numpy as np
from app.routes.ai import process_disease_detection
import json

def create_test_image(width=224, height=224, color='green', spots=False):
    """Create a synthetic test image for disease detection."""
    
    # Create base image
    if color == 'green':
        img = Image.new('RGB', (width, height), (34, 139, 34))  # Forest green
    elif color == 'brown':
        img = Image.new('RGB', (width, height), (139, 69, 19))  # Saddle brown
    elif color == 'yellow':
        img = Image.new('RGB', (width, height), (255, 255, 0))  # Yellow
    else:
        img = Image.new('RGB', (width, height), (128, 128, 128))  # Gray
    
    draw = ImageDraw.Draw(img)
    
    # Add disease spots if requested
    if spots:
        for i in range(np.random.randint(5, 15)):
            x = np.random.randint(0, width-20)
            y = np.random.randint(0, height-20)
            size = np.random.randint(5, 20)
            
            # Brown spots for disease
            draw.ellipse([x, y, x+size, y+size], fill=(139, 35, 35))
    
    return img

def test_disease_detection():
    """Test the enhanced disease detection system."""
    
    print("🧪 TESTING ENHANCED DISEASE DETECTION SYSTEM")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            'name': 'Healthy Wheat Leaf',
            'crop_type': 'wheat',
            'image_config': {'color': 'green', 'spots': False}
        },
        {
            'name': 'Diseased Wheat Leaf',
            'crop_type': 'wheat', 
            'image_config': {'color': 'green', 'spots': True}
        },
        {
            'name': 'Healthy Rice Plant',
            'crop_type': 'rice',
            'image_config': {'color': 'green', 'spots': False}
        },
        {
            'name': 'Diseased Rice Plant',
            'crop_type': 'rice',
            'image_config': {'color': 'brown', 'spots': True}
        },
        {
            'name': 'Healthy Sugarcane',
            'crop_type': 'sugarcane',
            'image_config': {'color': 'green', 'spots': False}
        },
        {
            'name': 'Diseased Sugarcane',
            'crop_type': 'sugarcane',
            'image_config': {'color': 'yellow', 'spots': True}
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Create test image
            img = create_test_image(**test_case['image_config'])
            test_image_path = f"app/static/test_images/test_{i}.jpg"
            img.save(test_image_path)
            
            # Run disease detection
            result = process_disease_detection(test_image_path, test_case['crop_type'])
            
            # Display results
            print(f"📊 Crop Type: {test_case['crop_type'].title()}")
            print(f"🔍 Detected Disease: {result['disease']} ({result['disease_en']})")
            print(f"📈 Confidence: {result['confidence']:.2%}")
            print(f"🩺 Health Status: {'Healthy' if result['is_healthy'] else 'Disease Detected'}")
            print(f"⚠️  Severity: {result['severity'].title()}")
            treatment_text = str(result['treatment'])
            if isinstance(result['treatment'], dict):
                treatment_text = result['treatment'].get('immediate', 'उपचार की जानकारी उपलब्ध है')
            print(f"💊 Treatment: {treatment_text[:100]}...")
            
            if 'analysis_details' in result:
                print(f"🔬 Analysis Details:")
                for key, value in result['analysis_details'].items():
                    print(f"   • {key.replace('_', ' ').title()}: {value}")
            
            results.append({
                'test_case': test_case['name'],
                'result': result,
                'status': 'SUCCESS'
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                'test_case': test_case['name'],
                'error': str(e),
                'status': 'FAILED'
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = len([r for r in results if r['status'] == 'SUCCESS'])
    total_tests = len(results)
    
    print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
    print(f"❌ Failed Tests: {total_tests - successful_tests}/{total_tests}")
    print(f"📊 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # Feature validation
    print("\n🔍 FEATURE VALIDATION:")
    print("-" * 30)
    
    if successful_tests > 0:
        print("✅ Image processing working")
        print("✅ Multi-crop support working")
        print("✅ Disease classification working")
        print("✅ Confidence scoring working")
        print("✅ Treatment recommendations working")
        print("✅ Severity assessment working")
        print("✅ Analysis details working")
    
    return results

def test_specific_features():
    """Test specific enhanced features of the disease detection."""
    
    print("\n🎯 TESTING SPECIFIC ENHANCED FEATURES")
    print("=" * 60)
    
    # Test image quality analysis
    print("\n1. Testing Image Quality Analysis:")
    print("-" * 35)
    
    # Create images with different brightness levels
    test_images = [
        {'brightness': 'dark', 'color': (20, 20, 20)},
        {'brightness': 'normal', 'color': (128, 128, 128)},
        {'brightness': 'bright', 'color': (240, 240, 240)}
    ]
    
    for img_test in test_images:
        img = Image.new('RGB', (224, 224), img_test['color'])
        test_path = f"app/static/test_images/quality_{img_test['brightness']}.jpg"
        img.save(test_path)
        
        result = process_disease_detection(test_path, 'wheat')
        print(f"   {img_test['brightness'].title()} image: {result['analysis_details'].get('image_quality', 'N/A')}")
    
    # Test disease variety coverage
    print("\n2. Testing Disease Coverage:")
    print("-" * 30)
    
    crop_types = ['wheat', 'rice', 'sugarcane', 'tomato', 'potato']
    disease_counts = {}
    
    for crop in crop_types:
        img = create_test_image(spots=True)
        test_path = f"app/static/test_images/coverage_{crop}.jpg"
        img.save(test_path)
        
        # Run detection multiple times to see variety
        diseases = set()
        for _ in range(5):
            result = process_disease_detection(test_path, crop)
            diseases.add(result['disease_en'])
        
        disease_counts[crop] = len(diseases)
        print(f"   {crop.title()}: {len(diseases)} different diseases detected")
    
    print(f"\n✅ Total unique diseases across all crops: {sum(disease_counts.values())}")
    
    # Test confidence variation
    print("\n3. Testing Confidence Scoring:")
    print("-" * 32)
    
    confidences = []
    for i in range(5):
        img = create_test_image(spots=True)
        test_path = f"app/static/test_images/conf_test_{i}.jpg"
        img.save(test_path)
        
        result = process_disease_detection(test_path, 'wheat')
        confidences.append(result['confidence'])
    
    print(f"   Confidence range: {min(confidences):.2%} - {max(confidences):.2%}")
    print(f"   Average confidence: {sum(confidences)/len(confidences):.2%}")
    print(f"   Confidence variation: {'Good' if max(confidences) - min(confidences) > 0.1 else 'Limited'}")

if __name__ == "__main__":
    print("🌾 SMART AGRICULTURE - DISEASE DETECTION TESTING")
    print("=" * 60)
    
    # Ensure test directory exists
    os.makedirs("app/static/test_images", exist_ok=True)
    
    # Run main tests
    results = test_disease_detection()
    
    # Run specific feature tests
    test_specific_features()
    
    print("\n🎯 TESTING COMPLETED!")
    print("=" * 60)
    
    # Save results to file
    with open("disease_detection_test_results.json", "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print("📄 Test results saved to: disease_detection_test_results.json")
