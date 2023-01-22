from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import pandas as pd

codes = [1240101,1240102,2240103,2240104,1240105,1240106,2240107,2240108,2240109,2240110
    ,2240111
    ,1240112
    ,1240113
    ,1240114
    ,2240115
    ,2240116
    ,2240117
    ,1240118
    ,1240119
    ,1240120
    ,1240121
    ,1240122
    ,1240123
    ,1240124
    ,2240125
    ,2240126
    ,2240127
    ,2240128]

def run(codes):
    for i in codes:
        user_name = 'user_' + str(i)
        user_email = 'user_' + str(i) + '@demo.ee'
        user_pwd = make_password(str(i))
        first_name = user_name
        last_name = 'demo'
        try:
            obj = User.objects.create(first_name=first_name,last_name=last_name,username=user_name,email=user_email,password=user_pwd)
            print(user_name+' '+user_pwd)
        except:
            print('error occurred.')
