from django.shortcuts import render ,redirect
from django.http import HttpResponse
from .models import Hotels,Rooms,Reservation
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
import datetime
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Hotels, Rooms, Reservation
from .serializers import HotelSerializer, RoomSerializer, ReservationSerializer

class HotelListAPIView(APIView):
    def get(self, request):
        hotels = Hotels.objects.all()
        serializer = HotelSerializer(hotels, many=True)
        return Response(serializer.data)

class RoomListAPIView(APIView):
    def get(self, request):
        rooms = Rooms.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

class ReservationListAPIView(APIView):
    def get(self, request):
        reservations = Reservation.objects.all()
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)

def homepage(request):
    # Получение всех доступных местоположений
    all_location = Hotels.objects.values_list('location', 'id', 'name').distinct().order_by()

    if request.method == "POST":
        try:
            print(request.POST)
            # Получение выбранного местоположения
            hotel = Hotels.objects.all().get(id=int(request.POST['search_location']))

            # Фильтрация номеров только по отелю
            room = Rooms.objects.all().filter(hotel=hotel)

            # Если номера не найдены, вывести предупреждение
            if len(room) == 0:
                messages.warning(request, "Извините, номера для выбранного местоположения отсутствуют.")

            # Подготовка данных для шаблона
            data = {'rooms': room, 'all_location': all_location, 'flag': True}
            response = render(request, 'index.html', data)
        except Exception as e:
            # Обработка ошибок
            messages.error(request, f"Произошла ошибка: {e}")
            response = render(request, 'index.html', {'all_location': all_location})
    else:
        # Для GET-запроса отображаем только список местоположений
        data = {'all_location': all_location}
        response = render(request, 'index.html', data)

    return response

def sign_up(request):
    if request.method == "POST":
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.warning(request, "Пароли не совпадают")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.warning(request, "Логин недоступен")
            return redirect('signup')

        is_staff = request.POST.get('is_staff') == 'on'  # Проверяем чекбокс
        new_user = User.objects.create_user(username=username, password=password1)
        new_user.is_superuser = False
        new_user.is_staff = is_staff
        new_user.save()

        messages.success(request, "Регистрация прошла успешно")
        login(request, new_user)
        return redirect("homepage")

    elif request.method == "GET":
        return render(request, "signup.html")  # Показываем форму

    return HttpResponse('Доступ запрещён')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Вход выполнен успешно")
            print("Login successfull")
            return redirect('homepage')
        else:
            messages.warning(request, "Неправильный логин или пароль")
            return redirect('login')

    response = render(request, 'login.html')
    return HttpResponse(response)

def logout_user(request):
    if request.method =='GET':
        logout(request)
        messages.success(request,"Выход из аккаунта прошел успешно")
        print("Logged out successfully")
        return redirect('homepage')
    else:
        print("Ошибка при выходе из аккаунта")
        return redirect('homepage')


@login_required(login_url='/staff')
def panel(request):
    if request.user.is_staff == False:
        return HttpResponse('Access Denied')
    
    rooms = Rooms.objects.all()
    hotels = Hotels.objects.all()
    total_rooms = len(rooms)
    available_rooms = len(Rooms.objects.all().filter(status='1'))
    unavailable_rooms = len(Rooms.objects.all().filter(status='2'))
    reserved = len(Reservation.objects.all())

    hotel = Hotels.objects.values_list('location','id', 'name').distinct().order_by()

    response = render(request,'staff/panel.html',{'location':hotel,'reserved':reserved,'rooms':rooms,'total_rooms':total_rooms,'available':available_rooms,'unavailable':unavailable_rooms, 'hotels': hotels})
    return HttpResponse(response)


@login_required(login_url='/staff')
def add_new_room(request):
    if request.user.is_staff == False:
        return HttpResponse('Access Denied')
    if request.method == "POST":

        hotel_id = request.POST.get('hotel')
        room_number = request.POST.get('roomnumber')

        # Проверяем наличие комнаты в этом отеле
        if Rooms.objects.filter(hotel_id=hotel_id, room_number=room_number).exists():
            messages.error(request, "Комната с таким номером уже существует в этом отеле.")
            return redirect('staffpanel')

        new_room = Rooms()
        hotel = Hotels.objects.all().get(id=int(request.POST['hotel']))
        new_room.room_number = request.POST['roomnumber']
        new_room.room_type = request.POST['roomtype']
        new_room.capacity = int(request.POST['capacity'])
        new_room.hotel = hotel
        new_room.status = request.POST['status']
        new_room.price = request.POST['price']

        new_room.save()
        messages.success(request,"Новая комната добавлена успешно")
    
    return redirect('staffpanel')

def book_room_page(request):
    room = Rooms.objects.all().get(id=int(request.GET['room_id']))
    return HttpResponse(render(request,'user/bookroom.html',{'room':room}))

def book_room(request):
    if request.method == "POST":

        check_in_date = datetime.strptime(request.POST['check_in'], "%Y-%m-%d")
        check_out_date = datetime.strptime(request.POST['check_out'], "%Y-%m-%d")

        # Проверка: дата выезда позже даты заезда
        if check_out_date <= check_in_date:
            messages.warning(request, "Дата выезда должна быть позже даты заезда!")
            return redirect("homepage")

        room_id = request.POST['room_id']
        room = Rooms.objects.get(id=room_id)

        # Даты из запроса
        new_check_in = request.POST['check_in']
        new_check_out = request.POST['check_out']

        # Проверка пересечения бронирований
        overlapping_reservations = Reservation.objects.filter(
            room=room,
            check_in__lt=new_check_out,  # Начало существующего бронирования раньше даты выезда нового бронирования
            check_out__gt=new_check_in  # Конец существующего бронирования позже даты заезда нового бронирования
        )

        if overlapping_reservations.exists():
            messages.warning(request, "Извините, этот номер недоступен для бронирования на выбранные даты")
            return redirect("homepage")

        # Если пересечений нет, продолжить обработку

        current_user = request.user

        reservation = Reservation()
        room_object = Rooms.objects.all().get(id=room_id)
        room_object.status = '2'

        user_object = User.objects.all().get(username=current_user)

        reservation.guest = user_object
        reservation.room = room_object
        reservation.person = int(request.POST['person'])
        reservation.check_in = request.POST['check_in']
        reservation.check_out = request.POST['check_out']

        reservation.save()

        messages.success(request, "Поздравляем! Бронирование прошло успешно.")
        return redirect("homepage")
    else:
        return HttpResponse('Доступ запрещён')


def handler404(request):
    return render(request, '404.html', status=404)

def user_bookings(request):
    if request.user.is_authenticated == False:
        return redirect('login')
    user = User.objects.all().get(id=request.user.id)
    print(f"request user id ={request.user.id}")
    bookings = Reservation.objects.all().filter(guest=user)
    if not bookings:
        messages.warning(request,"Бронирований не найдено")
    return HttpResponse(render(request,'user/mybookings.html',{'bookings':bookings}))

@login_required(login_url='/staff')
def add_new_location(request):
    if not request.user.is_staff:
        return HttpResponse("Доступ запрещён", status=403)
    if request.method == "POST":
        try:
            location = request.POST['new_city']
            name = request.POST['new_name']
        except KeyError:
            messages.error(request, "Не все данные предоставлены.")
            return redirect("staffpanel")
        # Проверка: есть ли отель с таким же названием и местоположением
        if Hotels.objects.filter(location=location, name=name).exists():
            messages.warning(request, "Отель с таким названием и местоположением уже существует!")
        else:
            # Добавляем новую запись
            Hotels.objects.create(location=location, name=name)
            messages.success(request, "Новое местоположение добавлено успешно!")
        return redirect("staffpanel")
    return HttpResponse("Неверный метод запроса", status=405)


@login_required(login_url='/staff')
def all_bookings(request):
   
    bookings = Reservation.objects.all()
    if not bookings:
        messages.warning(request,"Бронирований не найдено")
    return HttpResponse(render(request,'staff/allbookings.html',{'bookings':bookings}))


def cancel_booking(request, booking_id):
    # Получить бронирование или вернуть 404, если оно не существует
    reservation = get_object_or_404(Reservation, id=booking_id)
    reservation.delete()
    messages.success(request, "Бронирование успешно удалено.")
    return HttpResponseRedirect(reverse('homepage'))

@login_required(login_url='/staff')
def delete_room(request, room_number, location):
    room = get_object_or_404(Rooms, hotel=location, room_number=room_number)

    # Удаление номера
    room.delete()

    messages.success(request, "Номер успешно удален.")
    return HttpResponseRedirect(reverse('staffpanel'))


@login_required(login_url='/staff')
def delete_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotels, id=hotel_id)
    # Удаление номера
    hotel.delete()
    messages.success(request, "Отель успешно удален.")
    return HttpResponseRedirect(reverse('staffpanel'))