from django.db import migrations
from radar.models import AlienBody


default_alien_bodies_str = (
    '''\
--o-----o--
---o---o---
--ooooooo--
-oo-ooo-oo-
ooooooooooo
o-ooooooo-o
o-o-----o-o
---oo-oo---''',
    '''\
---oo---
--oooo--
-oooooo-
oo-oo-oo
oooooooo
--o--o--
-o-oo-o-
o-o--o-o''',
    '''\
-------o-------
-----ooooo-----
---oo--o--oo---
ooooooooooooooo
---oo-----oo---
--o--ooooo--o--
-oo---------oo-'''
)


def load_default_alien_bodies(apps, schema_editor):
    for alien_body_str in default_alien_bodies_str:
        AlienBody.objects.create(body_str=alien_body_str)


class Migration(migrations.Migration):

    dependencies = [
        ('radar', '0001_init_AlienBody'),
    ]

    operations = [
        migrations.RunPython(load_default_alien_bodies,
                             hints={'model_name': 'AlienBody'})
    ]
