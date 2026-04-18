import pandas as pd
from users.models import User,UserProfile
import random,string
import math
password_dict=dict()
def generate_password(length):
    # Generate a list of random characters
    characters = [random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(length)]
    # Shuffle the list of characters
    random.shuffle(characters)
    # Return the shuffled list of characters as a string
    return ''.join(characters)
def get_user(email,name:str):
    names=name.split(" ")
    try:
        if email:
            user=User.objects.get(email=email)
        else:
            user=User.objects.get(username__contains="".join(names))
    except User.DoesNotExist:

        
        user=User.objects.create(username="".join(names)+f"{random.randint(10,1000)}",
                                 #email=email,
                                 first_name=names[0],
                                password=generate_password(8))
        
        if email:
             user.email=email
             user.save()
    
    password_dict[name]=user.password
        
    return user
def set_or_null(cell):
     if not isinstance(cell,str):
        try:
            if cell and math.isnan(cell):
                return None
        except:
            return cell

     return cell

def get_row(row):
        coach_name=set_or_null(row["Coach Name"])
        coach_email=set_or_null(row['Email'])
        coach_desig=set_or_null(row["Designation"])
        coach_org=set_or_null(row["Organisation"] )
        coach_linkedin=set_or_null(row['LinkedIn'] )
        coach_pic=set_or_null(row['Picture'])
        try:
            coach_des=set_or_null(row['One Liner']) or ""
        except:
            coach_des=set_or_null(row['Description']) or ""

        coach_exp=set_or_null(row['Expertise'] )
        return {
             "name":coach_name,
             "email":coach_email,
             "designation":coach_desig,
             "company_name":coach_org,
             "linkedin":coach_linkedin,
             "profile_logo":coach_pic,
             "description":coach_des,
             "sector_of_expertise":coach_exp,
             "website":None,
             "location":set_or_null(row['Location'])

        }
        
def edit_create_profile(user,data,role):
    edited=False
    try:
         profile=UserProfile.objects.get(user=user,role=role)
         edited=True
    except:
         profile=UserProfile.objects.create(user=user,role=role)

    profile.name=data["name"]
    profile.google_email=data["email"]
    profile.description=data["description"]
    if data["sector_of_expertise"]:       
        profile.sector_of_expertise=data["sector_of_expertise"]
        profile.domain_of_expertise=data["sector_of_expertise"]
    profile.company_name=data['company_name']
    if data['linkedin']:     
        profile.linkedin=data["linkedin"]
    profile.profile_logo=data['profile_logo']
    profile.website=data['website']
    # profile.location=data['location']
    profile.save()
    return profile,edited



def run():
    df=pd.read_excel("scripts/Portal.xlsx",engine='openpyxl',sheet_name='Coaches')
    # print(df.head()["Organisation"])
    for index,row in df.iterrows():
         coach_data=get_row(row)
         user=get_user(coach_data["email"],coach_data["name"])
         coach_profile,edited=edit_create_profile(user,coach_data,"Coach")
         if not edited:
           print(f"{coach_profile.name} created")
         else:
                print(f"{coach_profile.name} edited")
    

    
        
         



       
        
    
