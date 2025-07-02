from core.models import Note
from felix.celery_app import app


@app.task
def add_note_to_customer(attached_to, content):
    # Adding note to the deal with user selected product details
    note = Note(
        attached_to=attached_to,
        note_type=Note.NOTE_TEXT,
        note_direction=Note.DIRECTION_IN,
        system_generated=True,
        content=content
    )

    note.save()
