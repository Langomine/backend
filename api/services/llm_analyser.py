from dataclasses import dataclass
from datetime import datetime
import pytz
from typing import Dict, List, TypedDict, Any
import json
from enum import Enum
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class ModelType(Enum):
    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"

class ScoreDetail(TypedDict):
    score: int
    description: str

class AnalysisResult(TypedDict):
    fluency: ScoreDetail
    lexical_richness: ScoreDetail
    grammar: ScoreDetail
    pronunciation: ScoreDetail
    overall: ScoreDetail
    model_used: str

@dataclass
class VoiceSegment:
    text: str
    start: float
    end: float

class LlmAnalyser:
    EUROPEAN_COUNTRIES = [
        "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
        "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
        "PL", "PT", "RO", "SK", "SI", "ES", "SE"
    ]

    ANALYSIS_FUNCTION = {
      "type": "json_schema",
      "json_schema": {
        "name": "ielts_speech_analysis",
        "description": "Detailed IELTS-aligned speech performance analysis",
        "schema": {
          "type": "object",
          "properties": {
            "fluency_and_coherence": {
              "type": "object",
              "description": "Evaluates the smooth flow of speech and logical organization of ideas",
              "properties": {
                "band_score": {
                  "type": "number",
                  "minimum": 1,
                  "maximum": 9,
                  "multipleOf": 0.5,
                  "description": "IELTS band score for fluency and coherence component (1-9)"
                },
                "strengths": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "List of positive aspects in speaker's fluency and coherence"
                },
                "areas_for_improvement": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "Specific areas where fluency and coherence can be enhanced"
                },
                "detailed_feedback": {
                  "type": "string",
                  "description": "Comprehensive analysis of fluency and coherence performance"
                }
              },
              "required": ["band_score", "strengths", "areas_for_improvement", "detailed_feedback"]
            },
            "lexical_resource": {
              "type": "object",
              "description": "Assesses vocabulary range, accuracy, and appropriateness",
              "properties": {
                "band_score": {
                  "type": "number",
                  "minimum": 1,
                  "maximum": 9,
                  "multipleOf": 0.5,
                  "description": "IELTS band score for lexical resource component (1-9)"
                },
                "vocabulary_analysis": {
                  "type": "object",
                  "description": "Detailed analysis of vocabulary usage",
                  "properties": {
                    "sophisticated_terms": {
                      "type": "array",
                      "items": {"type": "string"},
                      "description": "Advanced vocabulary words used in the speech"
                    },
                    "collocations": {
                      "type": "array",
                      "items": {"type": "string"},
                      "description": "Natural word combinations used correctly"
                    },
                    "idiomatic_expressions": {
                      "type": "array",
                      "items": {"type": "string"},
                      "description": "Native-like expressions and idioms used"
                    }
                  }
                },
                "detailed_feedback": {
                  "type": "string",
                  "description": "Comprehensive analysis of vocabulary usage and effectiveness"
                }
              },
              "required": ["band_score", "vocabulary_analysis", "detailed_feedback"]
            },
            "grammatical_range_and_accuracy": {
              "type": "object",
              "description": "Evaluates grammar usage, complexity, and correctness",
              "properties": {
                "band_score": {
                  "type": "number",
                  "minimum": 1,
                  "maximum": 9,
                  "multipleOf": 0.5,
                  "description": "IELTS band score for grammatical range and accuracy (1-9)"
                },
                "structure_analysis": {
                  "type": "object",
                  "description": "Analysis of grammatical structures used",
                  "properties": {
                    "complex_structures": {
                      "type": "array",
                      "items": {"type": "string"},
                      "description": "Advanced grammatical constructions used correctly"
                    },
                    "errors": {
                      "type": "array",
                      "items": {"type": "string"},
                      "description": "Grammatical mistakes identified in the speech"
                    }
                  }
                },
                "detailed_feedback": {
                  "type": "string",
                  "description": "Comprehensive analysis of grammatical performance"
                }
              },
              "required": ["band_score", "structure_analysis", "detailed_feedback"]
            },
            "pronunciation": {
              "type": "object",
              "description": "Assesses speech clarity, intonation, and sound production",
              "properties": {
                "band_score": {
                  "type": "number",
                  "minimum": 1,
                  "maximum": 9,
                  "multipleOf": 0.5,
                  "description": "IELTS band score for pronunciation component (1-9)"
                },
                "phonetic_analysis": {
                  "type": "object",
                  "description": "Detailed analysis of pronunciation features",
                  "properties": {
                    "clarity_score": {
                      "type": "number",
                      "minimum": 0,
                      "maximum": 1,
                      "description": "Overall clarity score between 0 and 1"
                    },
                    "problem_sounds": {
                      "type": "array",
                      "items": {"type": "string"},
                      "description": "Specific sounds that need improvement"
                    },
                    "intonation_patterns": {
                      "type": "array",
                      "items": {"type": "string"},
                      "description": "Analysis of speech rhythm and stress patterns"
                    }
                  }
                },
                "detailed_feedback": {
                  "type": "string",
                  "description": "Comprehensive analysis of pronunciation performance"
                }
              },
              "required": ["band_score", "phonetic_analysis", "detailed_feedback"]
            },
            "overall_assessment": {
              "type": "object",
              "description": "Complete evaluation of speaking performance",
              "properties": {
                "band_score": {
                  "type": "number",
                  "minimum": 1,
                  "maximum": 9,
                  "multipleOf": 0.5,
                  "description": "Final IELTS band score averaging all components"
                },
                "key_strengths": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "Main strong points across all assessment areas"
                },
                "priority_improvements": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "Critical areas requiring immediate attention"
                },
                "summary": {
                  "type": "string",
                  "description": "Overall performance summary and recommendations"
                }
              },
              "required": ["band_score", "key_strengths", "priority_improvements", "summary"]
            }
          },
          "required": ["fluency_and_coherence", "lexical_resource", "grammatical_range_and_accuracy", "pronunciation", "overall_assessment"]
        }
      }
    }

    def __init__(self, voice_content: List[Dict[str, str | float]], country_code: str) -> None:
        self.voice_content = voice_content
        self.country_code = country_code.upper()
        self.model = self._determine_model()
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def _determine_model(self) -> ModelType:
        if self.country_code in self.EUROPEAN_COUNTRIES:
            return ModelType.GPT4O
        return ModelType.GPT4O_MINI

    def _call_openai(self, prompt: str) -> str:
        response = self.openai_client.chat.completions.create(
            model=self.model.value,
            messages=[{"role": "user", "content": prompt}],
            response_format=self.ANALYSIS_FUNCTION,
        )

        return response.choices[0].message.content

    def analyze(self) -> any:
        prompt = f"""
        Analyze this speech text in detail:
        
        {self.voice_content}
        """
        response = self._call_openai(prompt)
        analysis = json.loads(response)
        analysis["model_used"] = self.model.value
        return analysis