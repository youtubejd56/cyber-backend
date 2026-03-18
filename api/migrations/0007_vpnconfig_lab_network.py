# Generated migration for lab_network field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_machineinstance_expires_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vpnconfig',
            name='lab_network',
            field=models.CharField(default='10.10.10.0/24', help_text='Lab network range (vulnerable machines)', max_length=50),
        ),
    ]
