from django.db import models

from db.models import BaseModel, CreatedUpdatedMixin


class Language(CreatedUpdatedMixin):
    name = models.CharField(max_length=255, unique=True, primary_key=True)

    def __str__(self):
        return self.name
