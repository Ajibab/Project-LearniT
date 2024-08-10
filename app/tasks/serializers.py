from .models import Quiz, TheoryQuiz,TheoryQuizAttempt,UserAttemptActivity,Answer,MultipleChoiceQuestions
from user.models import User
from typing import Dict, List
from rest_framework import serializers
from core.utilities.validators import is_admin,is_course_instructor
from lms.models import Module
from lms.serializers import DevelopModuleSerializer

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['module','description','creator','reattempt',]
        

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer

        fields = [
            'text',
            'question',
            'has_audio',
            'audio_record_answer',
        ]
        extra_kwargs = {
            "created_by": {"write_only": True}
        }

class MultipleChoiceQuestionSerializers(serializers.ModelSerializer):
    answers= serializers.SerializerMethodField()


    def get_answers(self, obj: MultipleChoiceQuestions):
        """ a serializer method to get the answer"""
        answers = Answer.objects.filter(question=obj.id)
        return AnswerSerializer(answers,many=True).data
    class Meta:
        fields = [
            'quiz',
            'answers'
            'prompt_question',
            'has_audio',
            'recorded_audio_question',
        ]
        model = MultipleChoiceQuestions

        extra_kwargs = {
            'quiz': {"read_only": True}
        }
class TheoryQuizSerializer(serializers.ModelSerializer):
    """ """
