"""
Notification Service - Handles SMS and other notifications
"""

from twilio.rest import Client
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications via SMS and other channels."""
    
    def __init__(self):
        self.account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        self.auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        self.phone_number = current_app.config.get('TWILIO_PHONE_NUMBER')
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not configured - SMS notifications disabled")
    
    def send_sms(self, phone_number, message, language='hi'):
        """
        Send generic SMS message.
        
        Args:
            phone_number (str): Recipient's phone number
            message (str): Message content
            language (str): Language preference ('hi' or 'en')
            
        Returns:
            dict: Result with status, message_id, and method
        """
        if not self.client:
            logger.info(f"SMS (Mock): {phone_number} - {message}")
            return {'status': 'success', 'message_id': 'mock_sms_123', 'method': 'mock'}
        
        try:
            # Send the message via Twilio
            sms_message = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=phone_number
            )
            
            logger.info(f"SMS sent successfully to {phone_number}, ID: {sms_message.sid}")
            return {
                'status': 'success',
                'message_id': sms_message.sid,
                'method': 'sms'
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'method': 'sms'
            }
    
    def send_irrigation_alert(self, user_phone, crop_name, message, language='hi'):
        """
        Send irrigation alert via SMS.
        
        Args:
            user_phone (str): User's phone number
            crop_name (str): Name of the crop
            message (str): Irrigation message
            language (str): Language preference ('hi' or 'en')
            
        Returns:
            dict: Notification result
        """
        if not self.client:
            logger.info(f"SMS Alert (Mock): {user_phone} - {message}")
            return {'status': 'success', 'message_id': 'mock_123', 'method': 'mock'}
        
        try:
            # Format message based on language
            if language == 'hi':
                formatted_message = f"""🌾 किसान साथी

फसल: {crop_name}
{message}

धन्यवाद,
स्मार्ट फसल देखभाल सहायक"""
            else:
                formatted_message = f"""🌾 Dear Farmer

Crop: {crop_name}
{message}

Thanks,
Smart Crop Care Assistant"""
            
            message = self.client.messages.create(
                body=formatted_message,
                from_=self.phone_number,
                to=user_phone
            )
            
            logger.info(f"SMS sent successfully to {user_phone}, ID: {message.sid}")
            return {
                'status': 'success',
                'message_id': message.sid,
                'method': 'sms'
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {user_phone}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'method': 'sms'
            }
    
    def send_weather_alert(self, user_phone, alert_type, message, language='hi'):
        """
        Send weather alert via SMS.
        
        Args:
            user_phone (str): User's phone number
            alert_type (str): Type of weather alert
            message (str): Alert message
            language (str): Language preference
            
        Returns:
            dict: Notification result
        """
        if not self.client:
            logger.info(f"Weather Alert (Mock): {user_phone} - {message}")
            return {'status': 'success', 'message_id': 'mock_456', 'method': 'mock'}
        
        try:
            # Weather alert icons
            icons = {
                'rain': '🌧️',
                'storm': '⛈️',
                'heat': '🌡️',
                'wind': '💨',
                'frost': '❄️'
            }
            
            icon = icons.get(alert_type, '⚠️')
            
            if language == 'hi':
                formatted_message = f"""{icon} मौसम चेतावनी

{message}

सावधान रहें,
स्मार्ट फसल देखभाल सहायक"""
            else:
                formatted_message = f"""{icon} Weather Alert

{message}

Stay safe,
Smart Crop Care Assistant"""
            
            message = self.client.messages.create(
                body=formatted_message,
                from_=self.phone_number,
                to=user_phone
            )
            
            logger.info(f"Weather alert sent to {user_phone}, ID: {message.sid}")
            return {
                'status': 'success',
                'message_id': message.sid,
                'method': 'sms'
            }
            
        except Exception as e:
            logger.error(f"Failed to send weather alert to {user_phone}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'method': 'sms'
            }
    
    def send_disease_alert(self, user_phone, crop_name, disease_name, confidence, treatment, language='hi'):
        """
        Send disease detection alert via SMS.
        
        Args:
            user_phone (str): User's phone number
            crop_name (str): Name of the crop
            disease_name (str): Detected disease name
            confidence (float): Detection confidence (0-100)
            treatment (str): Suggested treatment
            language (str): Language preference
            
        Returns:
            dict: Notification result
        """
        if not self.client:
            logger.info(f"Disease Alert (Mock): {user_phone} - {disease_name}")
            return {'status': 'success', 'message_id': 'mock_789', 'method': 'mock'}
        
        try:
            if language == 'hi':
                formatted_message = (
                    f"""🔍 रोग पहचान

फसल: {crop_name}
रोग: {disease_name}
सटीकता: {confidence:.0f}%

उपचार: {treatment}

तुरंत कार्रवाई करें,
स्मार���ट फसल देखभाल सहायक"""
                )
            else:
                formatted_message = (
                    f"""🔍 Disease Detection

Crop: {crop_name}
Disease: {disease_name}
Confidence: {confidence:.0f}%

Treatment: {treatment}

Take immediate action,
Smart Crop Care Assistant"""
                )
            
            message = self.client.messages.create(
                body=formatted_message,
                from_=self.phone_number,
                to=user_phone
            )
            
            logger.info(f"Disease alert sent to {user_phone}, ID: {message.sid}")
            return {
                'status': 'success',
                'message_id': message.sid,
                'method': 'sms'
            }
            
        except Exception as e:
            logger.error(f"Failed to send disease alert to {user_phone}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'method': 'sms'
            }
    
    def send_fertilizer_reminder(self, user_phone, crop_name, fertilizer_type, quantity, language='hi'):
        """
        Send fertilizer application reminder.
        
        Args:
            user_phone (str): User's phone number
            crop_name (str): Name of the crop
            fertilizer_type (str): Type of fertilizer
            quantity (str): Quantity to apply
            language (str): Language preference
            
        Returns:
            dict: Notification result
        """
        if not self.client:
            logger.info(f"Fertilizer Reminder (Mock): {user_phone} - {fertilizer_type}")
            return {'status': 'success', 'message_id': 'mock_101', 'method': 'mock'}
        
        try:
            if language == 'hi':
                formatted_message = (
                    f"""🌱 खाद अनुस्मारक

फसल: {crop_name}
खाद: {fertilizer_type}
मात्रा: {quantity}

आज डालें,
स्मार्ट फसल देखभाल सहायक"""
                )
            else:
                formatted_message = (
                    f"""🌱 Fertilizer Reminder

Crop: {crop_name}
Fertilizer: {fertilizer_type}
Quantity: {quantity}

Apply today,
Smart Crop Care Assistant"""
                )
            
            message = self.client.messages.create(
                body=formatted_message,
                from_=self.phone_number,
                to=user_phone
            )
            
            logger.info(f"Fertilizer reminder sent to {user_phone}, ID: {message.sid}")
            return {
                'status': 'success',
                'message_id': message.sid,
                'method': 'sms'
            }
            
        except Exception as e:
            logger.error(f"Failed to send fertilizer reminder to {user_phone}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'method': 'sms'
            }
    
    def send_bulk_notifications(self, notifications):
        """
        Send multiple notifications in bulk.
        
        Args:
            notifications (list): List of notification dictionaries
            
        Returns:
            dict: Summary of sent notifications
        """
        results = {
            'total': len(notifications),
            'sent': 0,
            'failed': 0,
            'details': []
        }
        
        for notification in notifications:
            if notification['type'] == 'irrigation':
                result = self.send_irrigation_alert(
                    notification['phone'],
                    notification['crop_name'],
                    notification['message'],
                    notification.get('language', 'hi')
                )
            elif notification['type'] == 'weather':
                result = self.send_weather_alert(
                    notification['phone'],
                    notification['alert_type'],
                    notification['message'],
                    notification.get('language', 'hi')
                )
            elif notification['type'] == 'disease':
                result = self.send_disease_alert(
                    notification['phone'],
                    notification['crop_name'],
                    notification['disease_name'],
                    notification['confidence'],
                    notification['treatment'],
                    notification.get('language', 'hi')
                )
            elif notification['type'] == 'fertilizer':
                result = self.send_fertilizer_reminder(
                    notification['phone'],
                    notification['crop_name'],
                    notification['fertilizer_type'],
                    notification['quantity'],
                    notification.get('language', 'hi')
                )
            else:
                result = {'status': 'error', 'error': 'Unknown notification type'}
            
            results['details'].append(result)
            
            if result['status'] == 'success':
                results['sent'] += 1
            else:
                results['failed'] += 1
        
        return results