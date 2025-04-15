from django.shortcuts import render, get_object_or_404
from .models import PersonOfHistory
from datetime import date
import hashlib


def person_of_the_day_view(request):
    """Display a repeatable person of history for each day."""
    all_persons = list(PersonOfHistory.objects.all())
    if not all_persons:
        return render(
            request,
            'peopleOfHistory/people_of_history.html',
            {'person': None})

    today_str = date.today().isoformat()  # z. B. "2025-04-15"
    hash_digest = hashlib.md5(today_str.encode()).hexdigest()
    hash_int = int(hash_digest, 16)

    index = hash_int % len(all_persons)
    person_of_the_day = all_persons[index]

    return render(
        request,
        'peopleOfHistory/people_of_history.html',
        {'person': person_of_the_day}
    )
