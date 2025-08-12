from datetime import date
from rest_framework.exceptions import ValidationError


def validate_user_is_adult(birthday):
    if not birthday:
        raise ValidationError("Дата рождения не указана.")

    today = date.today()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

    if age < 18:
        raise ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")
