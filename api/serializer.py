from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Voice, Question


class VoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = '__all__'

class AnalysedSerializer(serializers.Serializer):
    class FluencyAndCoherenceSerializer(serializers.Serializer):
        band_score = serializers.FloatField(min_value=1, max_value=9)
        strengths = serializers.ListField(child=serializers.CharField())
        areas_for_improvement = serializers.ListField(child=serializers.CharField())
        detailed_feedback = serializers.CharField()

    class LexicalResourceSerializer(serializers.Serializer):
        class VocabularyAnalysisSerializer(serializers.Serializer):
            sophisticated_terms = serializers.ListField(child=serializers.CharField())
            collocations = serializers.ListField(child=serializers.CharField())
            idiomatic_expressions = serializers.ListField(child=serializers.CharField())

        band_score = serializers.FloatField(min_value=1, max_value=9)
        vocabulary_analysis = VocabularyAnalysisSerializer()
        detailed_feedback = serializers.CharField()

    class GrammaticalRangeSerializer(serializers.Serializer):
        class StructureAnalysisSerializer(serializers.Serializer):
            complex_structures = serializers.ListField(child=serializers.CharField())
            errors = serializers.ListField(child=serializers.CharField())

        band_score = serializers.FloatField(min_value=1, max_value=9)
        structure_analysis = StructureAnalysisSerializer()
        detailed_feedback = serializers.CharField()

    class PronunciationSerializer(serializers.Serializer):
        class PhoneticAnalysisSerializer(serializers.Serializer):
            clarity_score = serializers.FloatField(min_value=0, max_value=1)
            problem_sounds = serializers.ListField(child=serializers.CharField())
            intonation_patterns = serializers.ListField(child=serializers.CharField())

        band_score = serializers.FloatField(min_value=1, max_value=9)
        phonetic_analysis = PhoneticAnalysisSerializer()
        detailed_feedback = serializers.CharField()

    class OverallAssessmentSerializer(serializers.Serializer):
        band_score = serializers.FloatField(min_value=1, max_value=9)
        key_strengths = serializers.ListField(child=serializers.CharField())
        priority_improvements = serializers.ListField(child=serializers.CharField())
        summary = serializers.CharField()

    fluency_and_coherence = FluencyAndCoherenceSerializer()
    lexical_resource = LexicalResourceSerializer()
    grammatical_range_and_accuracy = GrammaticalRangeSerializer()
    pronunciation = PronunciationSerializer()
    overall_assessment = OverallAssessmentSerializer()

# @extend_schema_serializer(
#     examples=[
#         OpenApiExample(
#             'Valid Analysis Response',
#             value={
#                 'fluency_and_coherence': {
#                     'band_score': 7.5,
#                     'strengths': ['Good flow'],
#                     'areas_for_improvement': ['Pausing'],
#                     'detailed_feedback': 'Good overall fluency'
#                 },
#                 # Add other sections as needed for the example
#             }
#         )
#     ]
# )
class ProcessedVoiceSerializer(serializers.ModelSerializer):
    analysed = AnalysedSerializer()

    class Meta:
        model = Voice
        fields = ['uuid', 'duration_s', 'text', 'file', 'language', 'created_at', 'analysed']

class VoiceUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class MainStatsSerializer(serializers.Serializer):
    # total_count = serializers.IntegerField()
    total_duration_s = serializers.IntegerField()

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'