from django.contrib import admin
from django.urls import path
import main.views as views
from django.urls import path
from main.views import HotelListAPIView, RoomListAPIView, ReservationListAPIView

urlpatterns = [
    path('', views.homepage,name="homepage"),
    path('home', views.homepage,name="homepage"),
    path('user/bookings', views.user_bookings,name="dashboard"),
    path('user/book-room', views.book_room_page,name="bookroompage"),
    path('user/book-room/book', views.book_room,name="bookroom"),
    path('staff/panel', views.panel,name="staffpanel"),
    path('staff/allbookings', views.all_bookings,name="allbookigs"),
    path('staff/panel/add-new-location', views.add_new_location,name="addnewlocation"),
    path('staff/panel/add-new-room', views.add_new_room,name="addroom"),
    path('admin/', admin.site.urls),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('delete-room/<int:location>/<int:room_number>/', views.delete_room, name='delete_room'),
    path('delete-hotel/<int:hotel_id>/', views.delete_hotel, name='delete_hotel'),
    path('signup', views.sign_up, name="signup"),
    path('login', views.login_user, name="login"),
    path('logout', views.logout_user,name="logout"),
    path('api/hotels/', HotelListAPIView.as_view(), name='api_hotels'),
    path('api/rooms/', RoomListAPIView.as_view(), name='api_rooms'),
    path('api/reservations/', ReservationListAPIView.as_view(), name='api_reservations'),
]
