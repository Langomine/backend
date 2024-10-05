import datetime
from pathlib import Path
import dateutil.parser
from dateutil.parser import ParserError
from django.core.files import File

from api.models import Voice
from api.tests.test_setup import TestSetUp
from django.utils import timezone


class TestViews(TestSetUp):
    def test_can_get_voice(self):
        voice = Voice(
            duration=datetime.timedelta(seconds=30),
            file=File(open(Path(__file__).absolute().parent / "assets/hi-there.mp3", mode="rb")),
        )

        voice.save()

        res = self.client.get(path=f"/api/voices/{voice.uuid}/", content_type='application/json')

        self.assertEqual(200, res.status_code)
        self.assertValidVoiceResponse(res.data, voice)

    def test_can_not_get_deleted_voice(self):
        voice = Voice(
            duration=datetime.timedelta(seconds=30),
            file=None,
            deleted_at=timezone.now(),
        )

        voice.save()

        res = self.client.get(path=f"/api/voices/{voice.uuid}/", content_type='application/json')

        self.assertEqual(404, res.status_code)

    def test_can_submit_voice(self):
        self.assertEqual(0, Voice.objects.count())

        res = self.client.post(path=f"/api/voices/", data={
            'file': File(open(Path(__file__).absolute().parent / "assets/hi-there.mp3", mode="rb"))
        })

        voice = Voice.objects.first()

        self.assertEqual(201, res.status_code)
        self.assertValidVoiceResponse(res.data, voice)

    def test_can_delete_voice(self):
        voice = Voice(
            duration=datetime.timedelta(seconds=30),
            file=File(open(Path(__file__).absolute().parent / "assets/hi-there.mp3", mode="rb")),
        )

        voice.save()

        res = self.client.delete(path=f"/api/voices/{voice.uuid}/")

        self.assertEqual(204, res.status_code)

        voice = Voice.objects.first()

        self.assertFalse(bool(voice.file))
        self.assertIsNotNone(voice.deleted_at)

    def assertValidVoiceResponse(self, data, voice: Voice):
        self.assertEqual(f"{voice.uuid}", data['uuid'])
        self.assertEqual(str(voice.duration).zfill(8), data['duration'])
        try:
            dateutil.parser.parse(data['created_at'])
        except ParserError:
            self.fail(f"{data['created_at']} is not a valid datetime format.")
