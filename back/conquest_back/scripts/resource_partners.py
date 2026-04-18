from .coach import edit_create_profile,set_or_null,generate_password,User,UserProfile
import random
import pandas as pd
def get_row(row):
    data={}
    data['company_name']=set_or_null(row['Organisation'])
    data['website']=set_or_null(row['Website'])
    data['profile_logo']=set_or_null(row['Logo'])
    data['description']=set_or_null(row['One Liner'])
    data['name']=set_or_null(row['POC Name'])
    data['email']=set_or_null(row['POC Mail'])
    data['linkedin']=set_or_null(row['POC Linkedin '])
    data['sector_of_expertise']=set_or_null(row['Category'])
    data['domain_of_expertise']=set_or_null(row['Offering'])#not creating new field for offering
    return data



def get_create_user(org,email):
    try:
       user=User.objects.get(username=org)
    except:
        user=User.objects.create(username=org)

    if email:
        user.email=email
        user.save()

    return user



def run():
    df=pd.read_excel("scripts/new_resources.xlsx",engine='openpyxl')
    
    print("=========================POPULATING Resource PARTNERS================================")

    for index,row in df.iterrows():

        data=get_row(row)
        user=get_create_user(data['company_name'],data['email'])
        profile,edited=edit_create_profile(user=user,data=data,role='Partner - Company')
        profile.offering=data['domain_of_expertise']
        profile.save()
        if edited:
            print(f'{profile.company_name} edited')
        else:
            print(f'{profile.company_name} created')


    


    


