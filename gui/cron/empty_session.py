from gui.models.user import UserSession
from django.contrib.auth import get_user_model


def emptySession():
    for user in get_user_model().objects.all():
        UserSession.objects.filter(
            pk__in=UserSession.objects.filter(user=user).order_by("-date").values_list('pk')[250:]
        ).delete()
