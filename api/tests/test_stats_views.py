import datetime
import json
from pathlib import Path
import dateutil.parser
from dateutil.parser import ParserError
from django.core.files import File
import responses

from api.models import Voice
from api.tests.test_setup import TestSetUp
from django.utils import timezone

from langomine.settings import OPEN_AI_WHISPERER_HOST


class TestStatsViews(TestSetUp):
    def test_can_get_stats(self):
        Voice(
            duration_s=30,
            file=File(open(Path(__file__).absolute().parent / "assets/hi-there.mp3", mode="rb")),
        ).save()

        Voice(
            duration_s=750,
            file=File(open(Path(__file__).absolute().parent / "assets/hi-there.mp3", mode="rb")),
        ).save()

        res = self.client.get(path=f"/api/stats/", content_type='application/json')

        self.assertEqual(200, res.status_code)
        # self.assertEqual(2, res.data['total_count'])
        self.assertEqual(780, res.data['total_duration_s'])
