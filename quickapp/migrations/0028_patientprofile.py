from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quickapp', '0027_alter_user_appointment_demail_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dob', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, max_length=20, null=True)),
                ('height_cm', models.IntegerField(blank=True, null=True)),
                ('weight_kg', models.IntegerField(blank=True, null=True)),
                ('blood_group', models.CharField(blank=True, max_length=5, null=True)),
                ('diabetes', models.BooleanField(default=False)),
                ('blood_pressure', models.BooleanField(default=False)),
                ('cholesterol', models.BooleanField(default=False)),
                ('ulcer', models.BooleanField(default=False)),
                ('heart_problem', models.BooleanField(default=False)),
                ('liver_problem', models.BooleanField(default=False)),
                ('brain_tumor', models.BooleanField(default=False)),
                ('cancer_related', models.BooleanField(default=False)),
                ('symptoms', models.CharField(blank=True, max_length=300, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='quickapp.usrdata')),
            ],
        ),
    ]


