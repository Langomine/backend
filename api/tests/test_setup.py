from django.test import override_settings
from rest_framework.test import APITestCase

@override_settings(STORAGES={
    "default": {
        "BACKEND": "django.core.files.storage.memory.InMemoryStorage",
    },
})
class TestSetUp(APITestCase):
    def setUp(self):
        return super().setUp()
    
    def tearDown(self):
        return super().tearDown()