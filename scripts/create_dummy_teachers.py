from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
def run():
    for i in range(10):
        user_name = 'teacher' + str(i)
        user_email = 'teacher' + str(i) + '@demo.ee'
        user_pwd = make_password("123abc4#")
        first_name = user_name
        last_name = 'ee'
        try:
            obj = User.objects.create(first_name=first_name,is_staff=True,last_name=last_name,username=user_name,email=user_email,password=user_pwd)
        except:
            print('error occurred.')
