# streamlit_app/app/entity_bridge/test_utils.py

import unittest
from utils import (
    generate_unique_identifier,
    calculate_similarity,
    normalize_text,
    log_normalization_actions
)

class TestUtils(unittest.TestCase):
    def test_generate_unique_identifier_uniqueness(self):
        """
        Test that each generated identifier is unique.
        """
        uid1 = generate_unique_identifier()
        uid2 = generate_unique_identifier()
        self.assertNotEqual(uid1, uid2)
        self.assertIsInstance(uid1, str)
        self.assertIsInstance(uid2, str)
        self.assertEqual(len(uid1), 36)  # UUID4 standard length
        self.assertEqual(len(uid2), 36)

    def test_calculate_similarity_identical(self):
        """
        Test similarity score for identical strings.
        """
        s1 = "OpenAI Corporation"
        s2 = "OpenAI Corporation"
        similarity = calculate_similarity(s1, s2)
        self.assertEqual(similarity, 1.0)

    def test_calculate_similarity_completely_different(self):
        """
        Test similarity score for completely different strings.
        """
        s1 = "OpenAI"
        s2 = "Microsoft"
        similarity = calculate_similarity(s1, s2)
        self.assertLess(similarity, 0.3)

    def test_calculate_similarity_partial_match(self):
        """
        Test similarity score for partially matching strings.
        """
        s1 = "Google LLC"
        s2 = "Google Inc."
        similarity = calculate_similarity(s1, s2)
        self.assertGreater(similarity, 0.7)

    def test_calculate_similarity_non_string_input(self):
        """
        Test that TypeError is raised when inputs are not strings.
        """
        with self.assertRaises(TypeError):
            calculate_similarity("OpenAI", 12345)
        with self.assertRaises(TypeError):
            calculate_similarity(None, "OpenAI")

    def test_normalize_text_basic(self):
        """
        Test basic normalization without custom stopwords.
        """
        text = "Apple Inc., based in Cupertino!"
        expected = "APPLE CUPERTINO"
        normalized = normalize_text(text)
        self.assertEqual(normalized, expected)

    def test_normalize_text_with_custom_stopwords(self):
        """
        Test normalization with additional custom stopwords.
        """
        text = "Apple Inc., based in Cupertino!"
        custom_stopwords = ['BASED']
        expected = "APPLE CUPERTINO"
        normalized = normalize_text(text, custom_stopwords=custom_stopwords)
        self.assertEqual(normalized, expected)

    def test_normalize_text_all_stopwords(self):
        """
        Test normalization where all words are stopwords.
        """
        text = "Inc. LLC Corp"
        expected = ""
        normalized = normalize_text(text)
        self.assertEqual(normalized, expected)

    def test_normalize_text_non_string_input(self):
        """
        Test that TypeError is raised when input text is not a string.
        """
        with self.assertRaises(TypeError):
            normalize_text(12345)
        with self.assertRaises(TypeError):
            normalize_text(None)

    def test_log_normalization_actions_basic(self):
        """
        Test basic logging of normalization actions.
        """
        actions_log = []
        log_normalization_actions(actions_log, "Converted to uppercase")
        self.assertIn("Converted to uppercase", actions_log)
        self.assertEqual(len(actions_log), 1)

    def test_log_normalization_actions_multiple(self):
        """
        Test logging multiple actions.
        """
        actions_log = []
        log_normalization_actions(actions_log, "Removed punctuation")
        log_normalization_actions(actions_log, "Eliminated stopwords")
        self.assertIn("Removed punctuation", actions_log)
        self.assertIn("Eliminated stopwords", actions_log)
        self.assertEqual(len(actions_log), 2)

    def test_log_normalization_actions_invalid_log(self):
        """
        Test that TypeError is raised when actions_log is not a list.
        """
        actions_log = "This is not a list"
        with self.assertRaises(TypeError):
            log_normalization_actions(actions_log, "Some action")

    def test_log_normalization_actions_invalid_description(self):
        """
        Test that TypeError is raised when action_description is not a string.
        """
        actions_log = []
        with self.assertRaises(TypeError):
            log_normalization_actions(actions_log, 12345)
        with self.assertRaises(TypeError):
            log_normalization_actions(actions_log, None)

if __name__ == '__main__':
    unittest.main()