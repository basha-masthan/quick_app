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


class usrData(models.Model):
    username = models.CharField(max_length=20,primary_key=True,unique=True)
    name=models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    mobile=models.IntegerField()
    password = models.CharField(max_length=30)


class user_appointment(models.Model):
    pusername=models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    demail = models.EmailField(max_length=30)
    pname=models.CharField(max_length=30)
    page=models.IntegerField()
    problem=models.CharField( max_length=150)
    day=models.DateField()
    time=models.CharField(max_length=50)