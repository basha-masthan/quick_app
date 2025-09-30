from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickapp', '0029_geofields'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor_data',
            name='map_embed',
            field=models.TextField(blank=True, null=True),
        ),
    ]


