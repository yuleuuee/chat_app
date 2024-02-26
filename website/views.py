from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

# from django.contrib.auth.forms import UserCreationForm
# from .forms import CustomUserCreationForm

from django.contrib.auth.models import User
from .models import UserProfile,Post,Like,FollowersCount

from datetime import datetime


from itertools import chain

# from django.contrib.auth.hashers import check_password,make_password

# Create your views here.

# # ------------------------------------------------------------------------------------------------------

def home(request):
    return render(request,'home.html',{})

# # --------------------------------- LOGIN -----------------------------------------------------------------------

def user_login(request):

    # user_profile = UserProfile.objects.get(user=request.user)
    # user_profile = UserProfile.objects.get(user=request.user)  # Access id to fetch

    
    if request.method == 'POST':
        u_name = request.POST['username']
        p_word = request.POST['password']

        #User.objects.filter(username=u_name).first()
        if User.objects.filter(username=u_name).exists(): # to check if the username is in the 'auth_user' table exists
            
            user = authenticate(request,username=u_name, password=p_word)

            if user is not None: # if there is user with  provided password matches the stored password
                login(request, user)
                messages.success(request, "Successfully logged in!")
                return redirect('public') #,{'user_profile':user_profile}
            else:
                messages.error(request, "Password Incorrect!")
                return redirect('login')
        else:
            messages.error(request, "User Doesn't Exist")
            return redirect('login')
    else:
        return render(request, 'login.html')
    
# ----------------------------------- SIGNUP -------------------------------------------------------------------
    
def user_signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('signup')
        elif pass1 == pass2:
            user = User.objects.create_user(username=username,email=email,password=pass1)
            user.save()

            #creating a UserProfile object for the New User: 
            # this means a row will be created for the 'New_user' in the 'UserProfile' table
            user_model = User.objects.get(username=username)
            new_UserProfile = UserProfile.objects.create(user =user_model) 
            new_UserProfile.save()

            messages.success(request, "Successfully registered")
            return redirect('login')
        else:
            messages.error(request, "Password dosn't match!")
            return redirect('signup')
    else:
        return render(request, 'signup.html') 
            
# ----------------------------------- LOGOUT -------------------------------------------------------------------
@login_required(login_url='login')
def user_logout(request):
    logout(request)
    messages.success(request,'Succesfully logged out!')
    return redirect('login')

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ----------------------------------------: FUNCTIONS :-------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def delete_account(request):
    if request.method == 'POST':
        confirm_pass = request.POST['confirm_pass']

         # Authenticate the user with entered password
        user = authenticate(username=request.user.username, password=confirm_pass)
        
        #Password is correct for the current user then
        if user is not None:
            user.delete()
            messages.success(request,'Succesfully Deleted Account!')
            return redirect('login')
        else:
            messages.error(request, "Password dosn't match!")
            return redirect('public')
    else:    
        # will never be this
        return redirect('public')
    

# ------------------------------------------------------------------------------------------------------


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']

        # Authenticate the user with entered old password
        user = authenticate(username=request.user.username, password=old_password)
        
        #Password is correct for the current user then
        if user is not None:
            if new_password1 == new_password2:
                user.set_password(new_password1)
                user.save()
                messages.success(request, "Password Successfully Changed")
                return redirect('public')
            else:
                messages.error(request, "New Passwords dosn't match!")
                return redirect('public')
        else:
            messages.error(request,'Old Password was Incorrect!, go to "Forgot password"')
            return redirect('public')
    else:    
        # will never be this
        return redirect('public')
    
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def public_page(request):

    user_profile = UserProfile.objects.get(user=request.user)
    # user_post, created = Post.objects.get_or_create(user=request.user)

    # posts = Post.objects.all()

    current_user = request.user
   
    current_time = datetime.now().time()
    #  today_date = datetime.now().date()
    # 'current_time': current_time,'today_date':today_date ,


    # ************ Show feeds of only following users and current user ***************

    user_following_list = []
    feed = []

    # Retrieve all posts of the current user
    my_posts = Post.objects.filter(user=request.user)

    # Include the posts of the current user in the feed
    feed.extend(my_posts)

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    # Retrieve User objects corresponding to the usernames
    for user_follow in user_following:
        user = get_object_or_404(User, username=user_follow.user)
        user_following_list.append(user)

    # Filter posts by the retrieved User objects
    for user in user_following_list:
        feed_lists = Post.objects.filter(user=user)
        feed.extend(feed_lists)


    # ****************************  User suggestions *********************************
    import random 

      # Get all users except the current user and the admin user
    all_users = User.objects.exclude(username=request.user.username).exclude(is_superuser=True)

    # Get the usernames of users whom the current user is following
    following_usernames = FollowersCount.objects.filter(follower=request.user.username).values_list('user', flat=True)

    # Exclude the users whom the current user is already following
    suggested_users = all_users.exclude(username__in=following_usernames)

    
    
     # Shuffle the suggested users and limiting the number of users shown
    suggested_users_subset = random.sample(list(suggested_users), min(len(suggested_users), 5))



    #**************************** greeting for the users *********************************
        

    if current_time.hour < 12:
        greeting = "Good morning"
    elif current_time.hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    
    context={
        'current_user': current_user, 
        'greeting': greeting ,
        'user_profile':user_profile,
        'posts': feed,
        'suggested_users': suggested_users_subset,
        
    }

    # ****************************** Searching Users *******************************
    

    query = request.GET.get('query')

    if query:
        search_results = User.objects.filter(username__icontains=query)
        if search_results.exists():
            # messages.success(request, 'Username was found successfully!')
            pass
        else:
            messages.error(request, 'Username does not match any existing user.')
    else:
        search_results = None

    context['search_results'] = search_results
    return render(request, 'public.html', context)

# ------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def settings(request):
    # current_user = request.user

    # this is the UserProfile Object, we can now assign value to the object's entities
    # object's entities includes : profile_picture,bio,phone
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        if request.FILES.get('new_profile_pic') == None: # if the user is'nt submitting profile picture, #getting the default profile pic from the media
            new_profile_pic =user_profile.profile_picture 
        else: # if the user is submitting a profile picture ,# getting from the uploaded file
            new_profile_pic =request.FILES.get('new_profile_pic') 

        if len(request.POST['new_phone_no']) == 0:
            new_phone_no = user_profile.phone
        else:
            new_phone_no = request.POST['new_phone_no']
        
        if len(request.POST['new_bio']) == 0:
            new_bio = user_profile.bio
        else:
            new_bio = request.POST['new_bio']

        # new_phone_no = request.POST['new_phone_no']
        # new_bio = request.POST['new_bio']
    
        user_profile.profile_picture = new_profile_pic
        user_profile.phone = new_phone_no
        user_profile.bio = new_bio

        user_profile.save()  # Saving the changes in UserProfile

        messages.success(request, " Save Change Success! ")
        # return render(request,'other_profile.html',{'user_profile':user_profile})

        return redirect('other_profile', pk=user_profile.user)
    else:
        return render(request,'settings.html',{'user_profile':user_profile})

    
# ------------------------------------------------------------------------------------------------------
@login_required(login_url='login')
def other_profile(request,pk):
    user_object = User.objects.get(username =pk)
    user_profile = UserProfile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user =user_profile.id) #getting the user_post info by using user_profile.id
    user_post_no = len(user_posts)


    follower = request.user.username
    user =pk

    # if the user was already followed then 
    if FollowersCount.objects.filter(follower=follower,user=user).first():
        button_text ='Unfollow'
    else:
        button_text ='Follow'

    # no. of followers and no. following
    user_followers = len(FollowersCount.objects.filter(user=pk)) # here the 'user : view' is the person that has been followed
    user_following = len(FollowersCount.objects.filter(follower=pk)) # here the 'follower : viewer' is the person that has been followed

    context={
        'user_object':user_object,
        'user_profile':user_profile,
        'user_posts':user_posts,
        'user_post_no' : user_post_no,
        'button_text':button_text,
        'user_followers':user_followers,
        'user_following':user_following,

    }

    return render(request,'other_profile.html',context)


# ------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def add_post(request):

    # user_post, created = Post.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user = request.user
        # post_img =request.FILES.get('post_img')
        # post_caption = request.POST['post_caption']

        if request.FILES.get('post_img') == None:
            messages.error(request, "Before posting, please make sure to upload an image!")
            return redirect('public')
        else:
           post_img =request.FILES.get('post_img')

        if len(request.POST['post_caption']) == 0:
            post_caption = 'No Caption'
        else:
            post_caption = request.POST['post_caption']

        new_post = Post.objects.create(user = user, image = post_img, caption = post_caption)
        
        # user_post.image = post_img
        # user_post.caption = post_caption

        new_post.save()
        messages.success(request, "Post Added Succesfully!")
        return redirect('public')

    else:    
        return redirect('public') # this helps to go the the view public_page ,as it is using the name of the url

# ------------------------------------------------------------------------------------------------------
    
@login_required(login_url='login')
def like_post(request):
    user = request.user
    post_id = request.GET.get('post_id') # getting the post id which was just  liked 

    post = Post.objects.get(id=post_id) # getting the post object which was liked by comparing the id

    like_filter = Like.objects.filter(post_id=post_id,user_id = user.id).first()

    if like_filter == None:
        new_like =Like.objects.create(post_id=post_id,user_id= user.id)
        new_like.save()
        post.no_of_likes=post.no_of_likes +1
        post.save()
        return redirect('public')
    else:
        like_filter.delete()
        post.no_of_likes=post.no_of_likes -1
        post.save()
        return redirect('public')
    
@login_required(login_url='login')
def follow(request):
    if request.method =='POST':
        #getting the information from the 'form'
        follower = request.POST['follower'] # Viewer : currently logged in user
        user = request.POST['user'] # view : user which the viewer is viewing

        # checking whether or not the currerently logged in user is already followeing this user
        # if already followed case :
        if FollowersCount.objects.filter(follower=follower,user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower,user=user)
            delete_follower.delete()
            return redirect('/other_profile/'+user) #going to the profile of the same user whch the viewer was viewing
        else: 
             # if already not followed case :
            new_follower = FollowersCount.objects.create(follower=follower,user=user)
            new_follower.save()
            return redirect('/other_profile/'+user) 
    else:
        return redirect('public')
    
# @login_required(login_url='login')
# def search_users(request):

#     pass
    
