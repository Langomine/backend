import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings

from api.services.llm_analyser import LlmAnalyser, ModelType
from unittest.mock import patch, MagicMock
from django.test import TestCase
from api.services.llm_analyser import LlmAnalyser, ModelType
import json

class TestLlmAnalyser(TestCase):
    def setUp(self):
        self.voice_content = [
            {"text": "Hello there", "start": 0.0, "end": 1.5},
            {"text": "How are you", "start": 1.5, "end": 2.5}
        ]
        self.mock_response = {
            "fluency_and_coherence": {
                "band_score": 7.0,
                "strengths": ["Good flow"],
                "areas_for_improvement": ["Pausing"],
                "detailed_feedback": "Good overall fluency"
            },
            "lexical_resource": {
                "band_score": 6.5,
                "vocabulary_analysis": {
                    "sophisticated_terms": ["term1"],
                    "collocations": ["coll1"],
                    "idiomatic_expressions": ["idiom1"]
                },
                "detailed_feedback": "Good vocabulary usage"
            },
            "grammatical_range_and_accuracy": {
                "band_score": 7.0,
                "structure_analysis": {
                    "complex_structures": ["structure1"],
                    "errors": ["error1"]
                },
                "detailed_feedback": "Good grammar"
            },
            "pronunciation": {
                "band_score": 6.5,
                "phonetic_analysis": {
                    "clarity_score": 0.8,
                    "problem_sounds": ["sound1"],
                    "intonation_patterns": ["pattern1"]
                },
                "detailed_feedback": "Clear pronunciation"
            },
            "overall_assessment": {
                "band_score": 6.5,
                "key_strengths": ["strength1"],
                "priority_improvements": ["improvement1"],
                "summary": "Good overall performance"
            }
        }

    @patch('api.services.llm_analyser.OpenAI')
    def test_analyze_european_country(self, mock_openai_class):
        # Setup mock
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.function_call.arguments = json.dumps(self.mock_response)
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        # Test European country (France)
        analyser = LlmAnalyser(self.voice_content, "FR")
        result = analyser.analyze()

        # Verify
        self.assertEqual(result["model_used"], ModelType.GPT4O.value)
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], ModelType.GPT4O.value)

    @patch('api.services.llm_analyser.OpenAI')
    def test_analyze_non_european_country(self, mock_openai_class):
        # Setup mock
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.function_call.arguments = json.dumps(self.mock_response)
        mock_choice.message = mock_message
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        # Test non-European country (United States)
        analyser = LlmAnalyser(self.voice_content, "US")
        result = analyser.analyze()

        # Verify
        self.assertEqual(result["model_used"], ModelType.GPT4O_MINI.value)
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], ModelType.GPT4O_MINI.value)
