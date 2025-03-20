import re
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr, constr, validator
import phonenumbers

class BookingValidationError(Exception):
    """Custom exception for booking validation errors"""
    pass

class SanitizedString(str):
    """Custom string type that removes potentially dangerous characters"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise ValueError('string required')
        # Remove potentially dangerous characters
        return cls(re.sub(r'[<>&;]', '', v))

class BookingRequest(BaseModel):
    """Enhanced booking request model with validation"""
    hotel_id: constr(min_length=1, max_length=100)
    check_in: str
    check_out: str
    guests: int
    room_type: SanitizedString
    name: SanitizedString
    email: EmailStr
    phone: str
    destination: SanitizedString
    adults: int
    children: int = 0
    preferences: Dict[str, bool] = {}

    @validator('guests')
    def validate_guests(cls, v):
        if v < 1:
            raise ValueError('At least one guest is required')
        if v > 10:
            raise ValueError('Maximum 10 guests allowed')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        try:
            phone_number = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(phone_number):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError('Invalid phone number format')

    @validator('check_in', 'check_out')
    def validate_dates(cls, v):
        try:
            date = datetime.strptime(v, "%Y-%m-%d")
            if date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                raise ValueError('Date cannot be in the past')
            return v
        except ValueError:
            raise ValueError('Invalid date format (YYYY-MM-DD)')

    @validator('preferences')
    def validate_preferences(cls, v):
        valid_preferences = {'breakfast', 'wifi', 'parking', 'pool', 'gym'}
        invalid_prefs = set(v.keys()) - valid_preferences
        if invalid_prefs:
            raise ValueError(f'Invalid preferences: {", ".join(invalid_prefs)}')
        return v

def sanitize_search_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize search parameters"""
    sanitized = {}
    
    # Sanitize destination
    if 'destination' in params:
        sanitized['destination'] = re.sub(r'[<>&;]', '', str(params['destination']))
    
    # Validate and sanitize dates
    for date_field in ['check_in', 'check_out']:
        if date_field in params:
            try:
                datetime.strptime(params[date_field], "%Y-%m-%d")
                sanitized[date_field] = params[date_field]
            except ValueError:
                raise ValueError(f'Invalid {date_field} date format')
    
    # Validate numeric fields
    for num_field in ['guests', 'price_range']:
        if num_field in params:
            try:
                value = float(params[num_field]) if num_field == 'price_range' else int(params[num_field])
                if value < 0:
                    raise ValueError(f'Invalid {num_field}: must be positive')
                sanitized[num_field] = value
            except ValueError:
                raise ValueError(f'Invalid {num_field} format')
    
    # Validate amenities
    if 'amenities' in params:
        valid_amenities = {'wifi', 'parking', 'pool', 'gym', 'restaurant', 'bar', 'spa'}
        if not isinstance(params['amenities'], list):
            raise ValueError('Amenities must be a list')
        sanitized['amenities'] = [
            amenity for amenity in params['amenities']
            if isinstance(amenity, str) and amenity in valid_amenities
        ]
    
    return sanitized

def validate_api_key(api_key: Optional[str]) -> bool:
    """Validate API key format"""
    if not api_key:
        return False
    # Check if it's a valid format (adjust pattern based on your API key format)
    return bool(re.match(r'^[A-Za-z0-9-_=]{32,}$', api_key))

def validate_hotel_id(hotel_id: str) -> bool:
    """Validate hotel ID format"""
    return bool(re.match(r'^[A-Za-z0-9-_]{1,100}$', hotel_id))

def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize sensitive data for logging"""
    sensitive_fields = {'email', 'phone', 'name', 'credit_card'}
    return {
        k: '***' if k in sensitive_fields else v
        for k, v in data.items()
    } 