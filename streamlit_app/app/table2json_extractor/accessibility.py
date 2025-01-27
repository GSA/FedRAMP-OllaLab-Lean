# accessibility.py

"""
accessibility.py

Module providing functionalities to ensure the application's accessibility compliance,
internationalization, and responsive design.

Includes functions and classes for:
- Applying accessibility features to the user interface.
- Supporting internationalization (i18n) and localization (l10n).
- Enhancing responsive design for different devices and screen sizes.
"""

import streamlit as st
from typing import Dict, Any, Optional
import gettext
import os
import logging

# Initialize logger
logger = logging.getLogger(__name__)

class AccessibilityManager:
    """
    Manages accessibility settings, internationalization, and responsive design for the application.
    """

    def __init__(self, locale_dir: str = 'locales', default_language: str = 'en'):
        """
        Initializes the AccessibilityManager.

        Parameters:
            locale_dir (str):
                Directory where the localization files are stored.
            default_language (str):
                The default language for the application.
        """
        self.locale_dir = locale_dir
        self.default_language = default_language
        self.current_language = default_language
        self.translations = {}
        self._load_translations()

    def _load_translations(self):
        """
        Loads translation files from the locales directory.
        """
        logger.debug("Loading translations.")
        try:
            languages = [d for d in os.listdir(self.locale_dir) if os.path.isdir(os.path.join(self.locale_dir, d))]
            for lang in languages:
                lang_dir = os.path.join(self.locale_dir, lang, 'LC_MESSAGES')
                mo_file = os.path.join(lang_dir, 'messages.mo')
                if os.path.exists(mo_file):
                    self.translations[lang] = gettext.GNUTranslations(open(mo_file, 'rb'))
                else:
                    logger.warning(f"No compiled translation file found for language '{lang}'.")
        except Exception as e:
            logger.exception(f"Error loading translations: {e}")
            raise

    def set_language(self, language: str):
        """
        Sets the current language for the application.

        Parameters:
            language (str):
                The language code to set (e.g., 'en', 'es', 'fr').

        Raises:
            ValueError:
                If the specified language is not available.
        """
        if language not in self.translations:
            logger.error(f"Language '{language}' not available.")
            raise ValueError(f"Language '{language}' not available.")
        self.current_language = language
        gettext.translation('messages', localedir=self.locale_dir, languages=[language]).install()
        logger.info(f"Language set to '{language}'.")

    def gettext(self, message: str) -> str:
        """
        Retrieves the translated message for the current language.

        Parameters:
            message (str):
                The message string to translate.

        Returns:
            str:
                The translated message.
        """
        translation = self.translations.get(self.current_language)
        if translation:
            return translation.gettext(message)
        else:
            return message  # Fall back to the original message

    def accessible_button(self, label: str, key: Optional[str] = None, help: Optional[str] = None, **kwargs) -> Any:
        """
        Creates an accessible button component with proper ARIA labels and translated text.

        Parameters:
            label (str):
                The label for the button.
            key (Optional[str]):
                An optional key for the button.
            help (Optional[str]):
                Help text for the button.

        Returns:
            Any:
                The value returned by the Streamlit button component.
        """
        translated_label = self.gettext(label)
        translated_help = self.gettext(help) if help else None
        return st.button(label=translated_label, key=key, help=translated_help, **kwargs)

    def accessible_text_input(self, label: str, value: str = "", key: Optional[str] = None, help: Optional[str] = None, **kwargs) -> str:
        """
        Creates an accessible text input component with proper ARIA labels and translated text.

        Parameters:
            label (str):
                The label for the text input.
            value (str):
                The default value of the text input.
            key (Optional[str]):
                An optional key for the text input.
            help (Optional[str]):
                Help text for the text input.

        Returns:
            str:
                The text entered by the user.
        """
        translated_label = self.gettext(label)
        translated_help = self.gettext(help) if help else None
        return st.text_input(label=translated_label, value=value, key=key, help=translated_help, **kwargs)

    def accessible_selectbox(self, label: str, options: list, index: int = 0, key: Optional[str] = None, help: Optional[str] = None, **kwargs) -> Any:
        """
        Creates an accessible selectbox component with proper ARIA labels and translated text.

        Parameters:
            label (str):
                The label for the selectbox.
            options (list):
                The options to display in the selectbox.
            index (int):
                The index of the pre-selected option.
            key (Optional[str]):
                An optional key for the selectbox.
            help (Optional[str]):
                Help text for the selectbox.

        Returns:
            Any:
                The selected option.
        """
        translated_label = self.gettext(label)
        translated_options = [self.gettext(option) for option in options]
        translated_help = self.gettext(help) if help else None
        return st.selectbox(label=translated_label, options=translated_options, index=index, key=key, help=translated_help, **kwargs)

    def apply_responsive_design(self):
        """
        Applies custom CSS to enhance the responsive design of the application.

        This function can be expanded to include additional CSS or dynamic adjustments
        based on the user's device or screen size.
        """
        logger.debug("Applying responsive design.")
        st.markdown(
            """
            <style>
            /* Custom CSS to improve responsiveness */
            @media only screen and (max-width: 600px) {
                /* Adjust font sizes for small screens */
                body {
                    font-size: 14px;
                }
                .stButton button {
                    width: 100%;
                }
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    def apply_accessibility_features(self):
        """
        Applies general accessibility features to the application, such as appropriate
        ARIA roles, labels, and keyboard navigation support.

        This function can be customized to enhance accessibility compliance as needed.
        """
        logger.debug("Applying general accessibility features.")
        # Currently, Streamlit handles many accessibility features internally.
        # Additional features can be added here as required.

    def collect_user_feedback(self):
        """
        Provides a mechanism for users to submit feedback about the application's
        accessibility and usability.

        Returns:
            None
        """
        st.sidebar.header(self.gettext("User Feedback"))
        feedback = st.sidebar.text_area(self.gettext("Please provide your feedback:"))
        if st.sidebar.button(self.gettext("Submit Feedback")):
            self.save_user_feedback(feedback)
            st.sidebar.success(self.gettext("Thank you for your feedback!"))

    def save_user_feedback(self, feedback: str):
        """
        Saves the user's feedback to a file or database.

        Parameters:
            feedback (str):
                The feedback provided by the user.

        Returns:
            None
        """
        logger.info("Saving user feedback.")
        # Implement the logic to save feedback to a file or database
        # For demonstration purposes, we'll append it to a text file
        with open('user_feedback.txt', 'a', encoding='utf-8') as f:
            f.write(f"{feedback}\n")