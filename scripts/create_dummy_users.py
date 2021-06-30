from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
def run():
    for i in range(50):
        user_name = 'user' + str(i)
        user_email = 'user' + str(i) + '@demo.ee'
        user_pwd = make_password("abc1234#")
        first_name = user_name
        last_name = 'demo'
        try:
            obj = User.objects.create(first_name=first_name,last_name=last_name,username=user_name,email=user_email,password=user_pwd)
        except:
            print('error occurred.')
