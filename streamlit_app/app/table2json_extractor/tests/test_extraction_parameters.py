# test_extraction_parameters.py

"""
Unit tests for the extraction_parameters.py module.
"""

import unittest
from extraction_parameters import (
    ExtractionParameters,
    TableSelectionCriteria,
    FormattingRules,
    ErrorHandlingStrategy,
    ParserConfiguration,
    ResourceLimits
)
from exceptions import InvalidParameterError

class TestExtractionParameters(unittest.TestCase):
    def test_valid_parameters(self):
        """
        Tests that valid parameters pass validation without raising exceptions.
        """
        table_selection = TableSelectionCriteria(
            method='indexing',
            indices=[0, 1, 2]
        )
        formatting_rules = FormattingRules(
            preserve_styles=True
        )
        data_types = {'Column1': str, 'Column2': int}
        error_handling = ErrorHandlingStrategy()
        parser_config = ParserConfiguration()
        extraction_params = ExtractionParameters(
            table_selection=table_selection,
            formatting_rules=formatting_rules,
            data_types=data_types,
            error_handling=error_handling,
            parser_config=parser_config
        )
        # Should not raise any exception
        extraction_params.validate_parameters()

    def test_invalid_table_selection_method(self):
        """
        Tests that an invalid table selection method raises an InvalidParameterError.
        """
        with self.assertRaises(InvalidParameterError):
            table_selection = TableSelectionCriteria(
                method='unknown_method'
            )
            table_selection.validate()

    def test_invalid_indices(self):
        """
        Tests that invalid indices raise an InvalidParameterError.
        """
        with self.assertRaises(InvalidParameterError):
            table_selection = TableSelectionCriteria(
                method='indexing',
                indices=['a', 'b']
            )
            table_selection.validate()

    def test_invalid_keywords(self):
        """
        Tests that invalid keywords raise an InvalidParameterError.
        """
        with self.assertRaises(InvalidParameterError):
            table_selection = TableSelectionCriteria(
                method='keyword',
                keywords=[123, 456]
            )
            table_selection.validate()

    def test_invalid_regex_patterns(self):
        """
        Tests that invalid regex patterns raise an InvalidParameterError.
        """
        with self.assertRaises(InvalidParameterError):
            table_selection = TableSelectionCriteria(
                method='regex',
                regex_patterns=['[invalid(regex']
            )
            table_selection.validate()

    def test_invalid_row_and_column_conditions(self):
        """
        Tests that missing conditions in 'criteria' method raise an InvalidParameterError.
        """
        with self.assertRaises(InvalidParameterError):
            table_selection = TableSelectionCriteria(
                method='criteria',
                row_conditions=None,
                column_conditions=None
            )
            table_selection.validate()

    def test_invalid_formatting_rules(self):
        """
        Tests that invalid formatting rules raise an InvalidParameterError.
        """
        with self.assertRaises(InvalidParameterError):
            formatting_rules = FormattingRules(
                preserve_styles='yes'  # Should be boolean
            )
            formatting_rules.validate()

        with self.assertRaises(InvalidParameterError):
            formatting_rules = FormattingRules(
                date_format='invalid_date_format'
            )
            formatting_rules.validate()

        with self.assertRaises(InvalidParameterError):
            formatting_rules = FormattingRules(
                encoding=123  # Should be string
            )
            formatting_rules.validate()

    def test_invalid_error_handling_strategy(self):
        """
        Tests that invalid error handling strategies raise an InvalidParameterError.
        """
        with self.assertRaises(InvalidParameterError):
            error_handling = ErrorHandlingStrategy(
                on_parsing_error='invalid_action'
            )
            error_handling.validate()

        with self.assertRaises(InvalidParameterError):
            error_handling = ErrorHandlingStrategy(
                on_validation_error='unknown_action'
            )
            error_handling.validate()

        with self.assertRaises(InvalidParameterError):
            error_handling = ErrorHandlingStrategy(
                fallback_mechanisms=['not_callable']
            )
            error_handling.validate()

    def test_invalid_parser_configuration(self):
        """
        Tests that invalid parser configurations raise an InvalidParameterError.
        """
        with self.assertRaises(InvalidParameterError):
            parser_config = ParserConfiguration(
                ocr_enabled='yes'  # Should be boolean
            )
            parser_config.validate()

        with self.assertRaises(InvalidParameterError):
            parser_config = ParserConfiguration(
                language=123  # Should be string
            )
            parser_config.validate()

    def test_invalid_resource_limits(self):
        """
        Tests that invalid resource limits raise an InvalidParameterError.
        """
        with self.assertRaises(InvalidParameterError):
            resource_limits = ResourceLimits(
                max_memory='a lot'  # Should be integer
            )
            resource_limits.validate()

        with self.assertRaises(InvalidParameterError):
            resource_limits = ResourceLimits(
                max_time=-10  # Should be positive integer
            )
            resource_limits.validate()

        with self.assertRaises(InvalidParameterError):
            resource_limits = ResourceLimits(
                max_cpu_usage=150  # Should be between 1 and 100
            )
            resource_limits.validate()

if __name__ == '__main__':
    unittest.main()