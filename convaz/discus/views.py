from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Room, Topic, Message, Profile
from .form import FormRoom, UserForm, ProfileForm

# Create your views here.

def page_login(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username = username)
        except:
            messages.error(request, 'This user does not exists')

        user = authenticate(request, username = username, password = password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exist')

    context = {'page': page}
    return render(request, 'discus/register_login.html', context)


def user_logout(request):
    logout(request)
    return redirect('home')
    

def register_user(request):
    #page = 'register'
    form = UserCreationForm()
    if request.method == 'POST':
        form =  UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('edit-user')
        else:
            messages.error(request, 'An error occured while registering')

    return render(request, 'discus/register_login.html', {'form': form})

@login_required(login_url='login')
def user_profile(request, pk):
    user = User.objects.get(id=pk)
    profile_img = Profile.objects.all()
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms':rooms, 'room_messages':room_messages, 
    'topics':topics, 'profile_img':profile_img}
    return render(request, 'discus/profile.html', context)  

@login_required(login_url='login')
def edit_user(request):
    user = request.user
    form = UserForm(instance=request.user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('upload-profile-img', pk=request.user)
    
    context = {'form':form}
    return render(request, 'discus/edit_user.html', context) 

def upload_profile_image(request, pk):
    profile_picture, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user = request.user
        form = ProfileForm(request.POST, request.FILES, instance=profile_picture)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)  # Redirect to profile page
    else:
        form = ProfileForm()
        user = request.user
        return render(request, 'discus/upload_profile_picture.html', {'form':form}) 

def home(request):
    qu = request.GET.get('qu') if request.GET.get('qu') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=qu) |
        Q(name__icontains=qu) |
        #Q(user__icontains=qu) |
        Q(description__icontains=qu)
        )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=qu))

    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages': room_messages}
    return render(request, 'discus/home.html', context)

@login_required(login_url='login')
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room':room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'discus/room.html', context)

@login_required(login_url='login')
def create_room(request):
    form = FormRoom()
    topic = Topic.objects.all()
    
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
       
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        #form = FormRoom(request.POST)
       # if form.is_valid():
        #    room = form.save(commit=False)
        #    room.host = request.user
        #   room.save()
        return redirect('home')

    context = {'form':form, 'topic':topic}
    return render(request, 'discus/form_room.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = FormRoom(instance=room)
    topic = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form':form, 'topic':topic, 'room':room}
    return render(request, 'discus/form_room.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method =="POST":
        room.delete()
        return redirect('home')
    return render(request, 'discus/delete.html', {'obj':room})

@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')

    if request.method =="POST":
        message.delete()
        return redirect('home')
    return render(request, 'discus/delete.html', {'obj':message})

def topic_page(request):
    qu = request.GET.get('qu') if request.GET.get('qu') != None else ''
    topics = Topic.objects.filter(name__icontains=qu)
    return render(request, 'discus/topics.html', {'topics':topics })


def activity_page(request):
    room_messages = Message.objects.all()
    return render(request, 'discus/activity.html', {'room_messages':room_messages})

