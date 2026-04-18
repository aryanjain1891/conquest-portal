import pandas as pd
import math
from users.models import UserProfile
from django.contrib.auth.models import User

def run():
    df = pd.read_excel("scripts/Portal.xlsx",sheet_name="Mentors") #change file path and sheet name
    list_of_records=df.to_dict(orient="records")

    for item in list_of_records:
        for field in item:
            if type(item[field])!=str:
                if math.isnan(item[field]):
                    item[field]=None
    
    print("POPULATING MENTORS.................")


    for field in list_of_records:
        try:
            user = User.objects.get(email=field['Email'])
        except User.DoesNotExist:
            user = User.objects.create(username=field['Mentor Name'],email=field['Email'])

        user_profile = UserProfile.objects.filter(user=user)
        if not user_profile:
            if not field['One Liner']:
                desc = " "
            else:
                desc = field["One Liner"]

            if not field['Expertise']:
                expertise = ""
            else:
                expertise= field["Expertise"]

            if not field['LinkedIn']:
                linkedin = ""
            else:
                linkedin = field['LinkedIn']

            if not field['Designation']:
                design = ""
            else:
                design = field['Designation']
                
            user_profile=UserProfile.objects.create(
                user = user,
                role = 'Mentor',
                google_email = field['Email'],
                name = field['Mentor Name'],   
                company_name = field['Organisation'],   
                linkedin = linkedin,   
                profile_logo = field['Picture'],   
                description = desc,   
                sector_of_expertise = expertise,   
                domain_of_expertise = expertise,
                designation = design,

            )
            print(f"{user_profile.name} created")

            
        else :
            user_profile.update(
                user = user,
                role = 'Mentor',
                google_email = field['Email'],
                name = field['Mentor Name'],   
                company_name = field['Organisation'],   
                linkedin = field['LinkedIn'],   
                profile_logo = field['Picture'],   
                description = field['One Liner' ],   
                sector_of_expertise = field['Expertise'],   
                domain_of_expertise = field['Expertise'],
                designation = field['Designation'],
            )
            print(f"{user_profile[0].name} edited")

            