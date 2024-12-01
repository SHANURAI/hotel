from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Hotels(models.Model):
    name = models.CharField(max_length=30, default=" ")
    location = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.location} ({self.name})"

class Rooms(models.Model):
    ROOM_STATUS = (
        ("1", "Доступен"),
        ("2", "Не доступен"),
    )
    ROOM_TYPE = (
        ("1", "Премиум"),
        ("2", "Комфорт"),
        ("3", "Стандарт"),
    )
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE)
    capacity = models.IntegerField()
    price = models.IntegerField()
    hotel = models.ForeignKey('Hotels', on_delete=models.CASCADE)
    status = models.CharField(choices=ROOM_STATUS, max_length=15)
    room_number = models.IntegerField()
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['hotel', 'room_number'], name='unique_room_per_hotel')
        ]
    def __str__(self):
        return f"{self.hotel.name} - Номер {self.roomnumber}"

class Reservation(models.Model):
    check_in = models.DateField(auto_now =False)
    check_out = models.DateField()
    room = models.ForeignKey(Rooms, on_delete = models.CASCADE)
    guest = models.ForeignKey(User, on_delete= models.CASCADE)
    def __str__(self):
        return self.guest.username


