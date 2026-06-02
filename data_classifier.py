"""
Core data classifier module for Chinese personal data.
Validates and classifies Chinese names, ID cards, and phone numbers.
"""

import csv
import re
from typing import List, Dict, Tuple


class DataClassifier:
    """Classifier for Chinese personal data."""
    
    # Valid phone prefixes (3-digit prefixes for 11-digit Chinese mobile numbers)
    VALID_PHONE_PREFIXES = {
        734, 735, 736, 737, 738, 739, 747, 748, 750, 751, 752, 757, 758, 759,
        772, 778, 782, 783, 784, 787, 788, 795, 798, 730, 731, 732, 740, 745,
        746, 755, 756, 766, 767, 771, 775, 776, 785, 786, 796, 733, 749, 753,
        773, 774, 777, 780, 781, 789, 790, 791, 793, 799
    }
    
    # ID card checksum coefficients
    ID_CARD_COEFFICIENTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    
    # Check digits for ID card (10 represents 'X')
    ID_CARD_CHECK_DIGITS = '10X98765432'
    
    @staticmethod
    def is_chinese_name(text: str) -> bool:
        """
        Check if text contains only Chinese characters.
        
        Args:
            text: The text to validate
            
        Returns:
            True if text contains only Chinese characters (\\u4e00-\\u9fff), False otherwise
        """
        if not text or not isinstance(text, str):
            return False
        
        # Check if all characters are Chinese (Unicode range \u4e00-\u9fff)
        pattern = r'^[\u4e00-\u9fff]+$'
        return bool(re.match(pattern, text))
    
    @staticmethod
    def is_valid_id_card(id_card: str) -> bool:
        """
        Validate an 18-digit Chinese ID card with checksum verification.
        
        Args:
            id_card: The ID card number to validate
            
        Returns:
            True if the ID card is valid, False otherwise
        """
        if not id_card or not isinstance(id_card, str):
            return False
        
        # ID card should be 18 characters
        if len(id_card) != 18:
            return False
        
        # First 17 characters should be digits, last can be digit or X
        if not id_card[:17].isdigit():
            return False
        
        if not (id_card[17].isdigit() or id_card[17].upper() == 'X'):
            return False
        
        # Calculate checksum
        total = 0
        for i in range(17):
            total += int(id_card[i]) * DataClassifier.ID_CARD_COEFFICIENTS[i]
        
        # Get check digit
        check_digit = DataClassifier.ID_CARD_CHECK_DIGITS[total % 11]
        
        # Verify check digit
        return id_card[17].upper() == check_digit
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """
        Validate an 11-digit Chinese phone number with valid prefix.
        
        Args:
            phone: The phone number to validate
            
        Returns:
            True if the phone number is valid, False otherwise
        """
        if not phone or not isinstance(phone, str):
            return False
        
        # Phone should be 11 digits
        if len(phone) != 11:
            return False
        
        # All characters should be digits
        if not phone.isdigit():
            return False
        
        # Check if prefix is valid
        prefix = int(phone[:3])
        return prefix in DataClassifier.VALID_PHONE_PREFIXES
    
    @staticmethod
    def classify_data(data_list: List[str]) -> List[Dict[str, str]]:
        """
        Classify each item in the list as Name, ID Card, Phone, or Unknown.
        
        Args:
            data_list: List of data items to classify
            
        Returns:
            List of dictionaries with 'data' and 'classification' keys
        """
        results = []
        
        for data in data_list:
            data = data.strip() if isinstance(data, str) else str(data)
            
            if not data:
                continue
            
            classification = 'Unknown'
            
            # Check in order: ID Card -> Phone -> Name -> Unknown
            if DataClassifier.is_valid_id_card(data):
                classification = 'ID Card'
            elif DataClassifier.is_valid_phone(data):
                classification = 'Phone'
            elif DataClassifier.is_chinese_name(data):
                classification = 'Name'
            
            results.append({
                'data': data,
                'classification': classification
            })
        
        return results
    
    @staticmethod
    def save_to_csv(results: List[Dict[str, str]], filename: str) -> bool:
        """
        Save classification results to a CSV file with UTF-8 encoding.
        
        Args:
            results: List of classification results
            filename: Output CSV filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['Data', 'Classification']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in results:
                    writer.writerow({
                        'Data': result['data'],
                        'Classification': result['classification']
                    })
            
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False
