from django.db import models
# Create your models here.
class Doctor_data(models.Model):
    fname=models.CharField(max_length=200,primary_key=True)
    lname=models.CharField(max_length=200)
    gender=models.CharField(max_length=20)
    email=models.EmailField(max_length=200,unique=True)
    mobile=models.IntegerField()
    specialization = models.CharField(max_length=200)
    hospital = models.CharField(max_length=200)
    mobile = models.IntegerField()
    price = models.CharField(max_length=10)
    address = models.CharField(max_length=500)
    password=models.CharField(max_length=30)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    map_embed = models.TextField(null=True, blank=True)


class usrData(models.Model):
    username = models.CharField(max_length=20,primary_key=True,unique=True)
    name=models.CharField(max_length=30)
    email = models.EmailField(max_length=40)
    mobile=models.IntegerField()
    password = models.CharField(max_length=30)


class user_appointment(models.Model):
    pusername=models.CharField(max_length=20,unique=True)
    gender = models.CharField(max_length=20)
    demail = models.EmailField(max_length=40)
    pname=models.CharField(max_length=30)
    page=models.IntegerField()
    problem=models.CharField( max_length=150)
    day=models.DateField()
    time=models.CharField(max_length=50)


class PatientProfile(models.Model):
    """Extended health profile for a registered patient (usrData)."""
    user = models.OneToOneField(usrData, on_delete=models.CASCADE, related_name='profile')
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    height_cm = models.IntegerField(null=True, blank=True)
    weight_kg = models.IntegerField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, null=True, blank=True)

    # Common health issues
    diabetes = models.BooleanField(default=False)
    blood_pressure = models.BooleanField(default=False)
    cholesterol = models.BooleanField(default=False)
    ulcer = models.BooleanField(default=False)

    # Serious health issues
    heart_problem = models.BooleanField(default=False)
    liver_problem = models.BooleanField(default=False)
    brain_tumor = models.BooleanField(default=False)
    cancer_related = models.BooleanField(default=False)

    symptoms = models.CharField(max_length=300, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"