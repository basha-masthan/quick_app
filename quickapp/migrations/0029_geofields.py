from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickapp', '0028_patientprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor_data',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='doctor_data',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='patientprofile',
            name='address',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='patientprofile',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='patientprofile',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]


