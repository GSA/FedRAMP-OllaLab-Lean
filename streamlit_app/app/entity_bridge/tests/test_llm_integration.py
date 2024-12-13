# streamlit_app/app/entity_bridge/tests/test_llm_integration.py

import unittest
from entity_bridge.llm_integration import parse_llm_output

class TestLLMIntegration(unittest.TestCase):

    def test_parse_llm_output_valid_json(self):
        output_text = '''
        {
            "groups": [
                {
                    "group_parent": "Alphabet Inc.",
                    "group_members": ["Google", "YouTube"]
                },
                {
                    "group_parent": "Facebook Inc.",
                    "group_members": ["Instagram", "WhatsApp"]
                }
            ]
        }
        '''
        expected_output = {
            "groups": [
                {
                    "group_parent": "Alphabet Inc.",
                    "group_members": ["Google", "YouTube"]
                },
                {
                    "group_parent": "Facebook Inc.",
                    "group_members": ["Instagram", "WhatsApp"]
                }
            ]
        }
        result = parse_llm_output(output_text)
        self.assertEqual(result, expected_output)

    def test_parse_llm_output_invalid_json(self):
        output_text = 'This is not valid JSON.'
        result = parse_llm_output(output_text)
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()