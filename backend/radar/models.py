from django.db import models


class AlienBody(models.Model):
    """
    Model that stores string representations of 'characters' on radar
    """
    body_str = models.CharField(max_length=225,     # 15 by 15 chars max
                                verbose_name='body string representation')
