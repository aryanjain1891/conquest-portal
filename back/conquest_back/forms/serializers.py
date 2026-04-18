from rest_framework import serializers
from .models import *

class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = ["id","form_name"]

class SubjectiveQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectiveQuestion
        fields = ["question","id","type"]

class FileUploadQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUploadQuestion
        fields = ["question","id"]

class ScoringQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoringQuestion
        fields = ["question","id"]

class PreferenceQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreferenceQuestion
        fields = ["question","id"]

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = ["preference_name","id"]

class SubjectiveAnsSerializer(serializers.ModelSerializer):
    # tracks = serializers.PrimaryKeyRelatedField()
    class Meta:
        model = SubjectiveAns
        fields = ["answer","subjective_question","under_answer"]
