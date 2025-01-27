# locale_manager.py

"""
locale_manager.py

This module provides a LocaleManager class to handle locale-specific formatting and parsing of dates,
numbers, currencies, etc., without changing the global locale settings of the application.

It relies on the 'babel' library to provide locale-aware formatting and parsing functionalities.

Dependencies:
- Babel (install via pip install Babel)

Usage:
    from locale_manager import LocaleManager

    locale_manager = LocaleManager('en_US')

    formatted_date = locale_manager.format_date(datetime.now())
    parsed_date = locale_manager.parse_date('Dec 31, 2021')

    formatted_number = locale_manager.format_number(123456.789)
    parsed_number = locale_manager.parse_number('123,456.789')

    formatted_currency = locale_manager.format_currency(1234.56, 'USD')
"""

import logging
from babel import Locale, dates, numbers
from typing import List, Optional
from datetime import datetime, date

# Configure logging
logger = logging.getLogger(__name__)

# Define custom exceptions for locale-related errors
class LocaleError(Exception):
    """Base exception for locale errors."""
    pass

class InvalidLocaleError(LocaleError):
    """Raised when an invalid or unsupported locale is specified."""
    pass

class LocaleManager:
    """
    Manages locale-specific formatting and parsing of dates, numbers, and currencies.
    Uses the Babel library to perform locale-aware operations.

    Attributes:
        locale_name (str): The locale identifier (e.g., 'en_US', 'fr_FR').

    Methods:
        format_date(date_obj): Formats a date object according to the locale.
        parse_date(date_str): Parses a date string according to the locale.
        format_number(number): Formats a number according to the locale.
        parse_number(number_str): Parses a number string according to the locale.
        format_currency(number, currency): Formats a currency amount according to the locale.
        get_available_locales(): Returns a list of available locale identifiers.
    """

    def __init__(self, locale_name: str):
        """
        Initialize the LocaleManager with the specified locale.

        Parameters:
            locale_name (str): The locale identifier (e.g., 'en_US', 'fr_FR').

        Raises:
            InvalidLocaleError: If the specified locale is not available.
        """
        self.logger = logging.getLogger(__name__)
        self.locale_name = locale_name
        try:
            self.locale = Locale.parse(locale_name)
        except ValueError as e:
            self.logger.error(f"Invalid locale '{locale_name}': {e}")
            raise InvalidLocaleError(f"Invalid locale '{locale_name}': {e}")

    def format_date(self, date_obj: datetime, date_format: str = 'medium') -> str:
        """
        Formats a date object according to the locale.

        Parameters:
            date_obj (datetime): The date object to format.
            date_format (str): The format to use ('short', 'medium', 'long', 'full', or custom pattern).

        Returns:
            str: The formatted date string.

        Raises:
            ValueError: If date_format is invalid.
        """
        try:
            formatted_date = dates.format_date(date_obj, format=date_format, locale=self.locale)
            return formatted_date
        except Exception as e:
            self.logger.error(f"Error formatting date: {e}")
            raise ValueError(f"Error formatting date: {e}")

    def parse_date(self, date_str: str, date_format: Optional[str] = None) -> date:
        """
        Parses a date string according to the locale.

        Parameters:
            date_str (str): The date string to parse.
            date_format (Optional[str]): The format to use (e.g., 'short', 'medium', 'long', 'full', or custom pattern).
                                         If None, attempts to parse using locale's default formats.

        Returns:
            datetime.date: The parsed date object.

        Raises:
            ValueError: If the date string cannot be parsed.
        """
        try:
            if date_format:
                date_obj = dates.parse_date(date_str, format=date_format, locale=self.locale)
            else:
                # Try default formats
                for fmt in ['short', 'medium', 'long', 'full']:
                    try:
                        date_obj = dates.parse_date(date_str, format=fmt, locale=self.locale)
                        return date_obj
                    except:
                        continue
                raise ValueError(f"Unable to parse date string '{date_str}' with locale '{self.locale_name}'.")
            return date_obj
        except Exception as e:
            self.logger.error(f"Error parsing date string '{date_str}': {e}")
            raise ValueError(f"Error parsing date string '{date_str}': {e}")

    def format_number(self, number, number_format: Optional[str] = None) -> str:
        """
        Formats a number according to the locale.

        Parameters:
            number (float or int): The number to format.
            number_format (Optional[str]): A custom format pattern.

        Returns:
            str: The formatted number string.

        Raises:
            ValueError: If formatting fails.
        """
        try:
            formatted_number = numbers.format_decimal(number, format=number_format, locale=self.locale)
            return formatted_number
        except Exception as e:
            self.logger.error(f"Error formatting number: {e}")
            raise ValueError(f"Error formatting number: {e}")

    def parse_number(self, number_str: str) -> float:
        """
        Parses a number string according to the locale.

        Parameters:
            number_str (str): The number string to parse.

        Returns:
            float: The parsed number.

        Raises:
            ValueError: If the number string cannot be parsed.
        """
        try:
            number = numbers.parse_decimal(number_str, locale=self.locale)
            return number
        except Exception as e:
            self.logger.error(f"Error parsing number string '{number_str}': {e}")
            raise ValueError(f"Error parsing number string '{number_str}': {e}")

    def format_currency(self, number, currency: str) -> str:
        """
        Formats a currency amount according to the locale.

        Parameters:
            number (float or int): The currency amount.
            currency (str): The currency code (e.g., 'USD', 'EUR').

        Returns:
            str: The formatted currency string.

        Raises:
            ValueError: If formatting fails.
        """
        try:
            formatted_currency = numbers.format_currency(number, currency, locale=self.locale)
            return formatted_currency
        except Exception as e:
            self.logger.error(f"Error formatting currency: {e}")
            raise ValueError(f"Error formatting currency: {e}")

    @staticmethod
    def get_available_locales() -> List[str]:
        """
        Returns a list of available locale identifiers.

        Returns:
            List[str]: A list of locale identifiers.
        """
        locales = Locale.available_locales()
        locale_identifiers = [str(loc) for loc in locales]
        return locale_identifiers