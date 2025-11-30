from django.shortcuts import render

from rest_framework  import generics
from .models import Room

from .serializers import RoomSerializer
#end points are what comes after a slash in a url and takes you somewhere on the web 
# Create your views here.

class RoomView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class= RoomSerializer


 
