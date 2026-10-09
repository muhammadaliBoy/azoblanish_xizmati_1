import random

from django.conf import settings
from django.core.mail import send_mail
from rest_framework.serializers import ValidationError

from .models import EmailCode

ERROR = "Kod topilmadi, muddati tugagan yoki urinishlar tugagan"
NOT_CONFIRMED = "Avval kodni tasdiqlang yoki kod muddati tugagan"


def send_verification_code(user):
    code = str(random.randint(100000, 999999))    # 6 xonali kod

    # faqat oxirgi kod ishlaydi
    EmailCode.objects.filter(user=user).delete()
    EmailCode.objects.create(user=user, code=code)

    send_mail(
        "Tasdiqlash kodi",
        f"Kodingiz: {code}\n5 daqiqa amal qiladi.",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )


def confirm_code(user, code):
    record = EmailCode.objects.filter(user=user).first()

    if record is None or record.is_expired():
        raise ValidationError({"detail": ERROR})
    if record.attempts >= EmailCode.MAX_ATTEMPTS:
        raise ValidationError({"detail": ERROR})

    if record.code != code:
        record.attempts += 1
        record.save()
        raise ValidationError({"detail": "Kod noto'g'ri"})

    record.is_confirmed = True
    record.save()


def finish_code(user):
    record = EmailCode.objects.filter(
        user=user, is_confirmed=True
    ).first()

    if record is None or record.is_expired():
        raise ValidationError({"detail": NOT_CONFIRMED})

    record.delete()

from django.contrib.auth import get_user_model
from django.core import signing
from rest_framework.serializers import ValidationError

User = get_user_model()
SALT = "pre-token"
ERROR = "pre_token yaroqsiz yoki muddati tugagan"


def make_pre_token(user_id):
    # SECRET_KEY bilan imzolanadi — soxtalab bo'lmaydi
    return signing.dumps({"user_id": user_id}, salt=SALT)


def get_user(pre_token):
    try:
        data = signing.loads(pre_token, salt=SALT, max_age=1800)
        user_id = data["user_id"]            # 30 daqiqa yashaydi
    except signing.BadSignature:
        user_id = None

    user = User.objects.filter(id=user_id).first()
    if user is None:
        raise ValidationError({"detail": ERROR})
    return user