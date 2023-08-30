import json
import time

import pandas as pd
# import requests
# from algorithm.auto_password_generator import generate_password
# from authentication.models import User
# from django.contrib.auth.hashers import make_password
# from algorithm.username_generator import auto_user
def create_broker_dataset(file_path):
    data = pd.read_csv(file_path, delimiter=',')
    list_of_csv = [list(row) for row in data.values]
    for l in list_of_csv:
        # if type(l[0]) == float:
        #     continue
        # qs = User.objects.all()
        # email = l[22]
        # email_list = []
        # for user in qs:
        #     email_qs = user.email
        #     email_list.append(email_qs)
        # if email in email_list:
        #     return False
        # URL = l[0]
        # ZPID = l[1]
        # first_name = l[17]
        # last_name = l[19]
        # phone_number = l[20]
        # zuid = l[21]
        # address = l[23]
        # profile_pic = l[24]
        # print(l[23], l[24])
        # password = generate_password()
        # username = auto_user(email)
        # if type(profile_pic) == float:
        #     profile_pic = None

        print(l)
        # Make Email from broker that new user
    
        time.sleep(1)


create_broker_dataset('xyz.csv')