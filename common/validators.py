from datetime import date, datetime
from rest_framework import serializers


def validate_user_is_adult(birthday):
    if not birthday:
        raise serializers.ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")

    if isinstance(birthday, str):
        birthday = datetime.strptime(birthday, "%Y-%m-%d").date()

    today = date.today()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

    if age < 18:
        raise serializers.ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")
