from django.urls import path, re_path

from .views.voices import VoiceView
from .views.stats import StatView

urlpatterns = [
    path('stats/', StatView.as_view({
        'get': 'show'
    })),

    path('voices/', VoiceView.as_view({
        'post': 'store'
    })),

    path('voices/<uuid:uuid>/', VoiceView.as_view({
        'get': 'show',
        'delete': 'destroy',
    })),

    # path('voices', VoiceView.store, name='voices.store'),
    # path('voices/<str:pk>', VoiceView.show, name='voices.store'),
    # path('voices/<str:pk>', delete, name='voices.delete'),
]

