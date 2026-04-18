import pandas as pd
from users.models import User,UserProfile
from .coach import set_or_null

def get_data(row):
    return {
        'company_name':set_or_null(row['Company']),
        'profile_logo':set_or_null(row['Logo']),
        'description':set_or_null(row['Description']),
        'website':set_or_null(row['Website']),
        'no_of_calls':set_or_null(row['No of Calls']),
        'comments':set_or_null(row['Comments']),
    }
def get_create_user(company_name :str):
    try:
        user=User.objects.get(username=company_name.split(" ")[0],email='defaultemail@gmail.com')
    except:
        user=User.objects.create_user(username=company_name.split(" ")[0],password=User.objects.make_random_password(10),email='defaultemail@gmail.com')

    return user

def get_create_profile(user,data):
    edited=False
    try:
        profile=UserProfile.objects.get(user=user)
        edited=True
    except:
        profile=UserProfile.objects.create(user=user)

    profile.role='Consultant'
    profile.name=data['company_name']
    profile.description=data['description']
    profile.no_of_calls=data['no_of_calls']
    profile.website=data['website']
    profile.comments=data['comments']
    profile.company_name=data['company_name']
    if len(data['profile_logo'])<500:
        profile.profile_logo=data['profile_logo']

    profile.save()
    return profile,edited





def run():
    df=pd.read_excel("scripts/consultants.xlsx",engine='openpyxl',sheet_name='Sheet1')
    
    for index,row in df.iterrows():
        data=get_data(row)
        user=get_create_user(data['company_name'])
        profile,edited=get_create_profile(user,data)

        if edited:
            print(profile.name+" edited")
        else:
            print(profile.name+" created")
