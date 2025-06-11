from django.shortcuts import render, get_object_or_404
from .models import PersonOfHistory
from datetime import date
import hashlib
from cloudinary.utils import cloudinary_url


def person_of_the_day_view(request):
    """Display a repeatable person of history for each day."""
    all_persons = list(PersonOfHistory.objects.all())
    if not all_persons:
        return render(
            request,
            'peopleOfHistory/people_of_history.html',
            {'person_of_history': None}
        )

    today_str = date.today().isoformat()
    hash_digest = hashlib.md5(today_str.encode()).hexdigest()
    hash_int = int(hash_digest, 16)

    index = hash_int % len(all_persons)
    person_of_the_day = all_persons[index]
    secure_url, _ = cloudinary_url(
        person_of_the_day.image.public_id,
        secure=True,
        transformation=[
            {"width": 300, "crop": "scale"},
            {"quality": "auto"},
            {"fetch_format": "auto"}
        ]
    )

    return render(
        request,
        'peopleOfHistory/people_of_history.html',
        {
            'person_of_history': person_of_the_day,
            'secure_image_url': secure_url
        }
    )
