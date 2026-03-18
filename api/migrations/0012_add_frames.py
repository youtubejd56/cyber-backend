# Generated migration for Frames feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_add_completed_machines'),
    ]

    operations = [
        # Add frame fields to UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='frame',
            field=models.CharField(default='default', max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='unlocked_frames',
            field=models.JSONField(default=list),
        ),
        
        # Create Frame model
        migrations.CreateModel(
            name='Frame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frame_id', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('required_points', models.IntegerField()),
                ('border_color', models.CharField(default='#cd7f32', max_length=20)),
                ('gradient_start', models.CharField(default='#cd7f32', max_length=20)),
                ('gradient_end', models.CharField(default='#8b4513', max_length=20)),
                ('icon', models.CharField(default='🏅', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
