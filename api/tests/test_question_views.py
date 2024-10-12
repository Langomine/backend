import datetime
import json
from pathlib import Path
import dateutil.parser
from dateutil.parser import ParserError
from django.core.files import File
import responses

from api.models import Voice, Question
from api.tests.test_setup import TestSetUp
from django.utils import timezone

from langomine.settings import OPEN_AI_WHISPERER_HOST


class TestQuestionViews(TestSetUp):
    def test_can_list_questions(self):
        Question(
            id=1,
            text="Question 1"
        ).save()

        Question(
            id=2,
            text="Question 2"
        ).save()

        res = self.client.get(path=f"/api/questions/", content_type='application/json')

        self.assertEqual(200, res.status_code)
        self.assertEqual(2, len(res.data))

        self.assertDictEqual({
            'id': 1,
            'text': 'Question 1',
        }, res.data[0])
        self.assertDictEqual({
            'id': 2,
            'text': 'Question 2',
        }, res.data[1])