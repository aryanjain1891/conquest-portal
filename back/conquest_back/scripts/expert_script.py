import pandas as pd
import math
from users.models import UserProfile
from django.contrib.auth.models import User
from django.db.models import Q


def run():
    df = pd.read_excel("scripts/Portal.xlsx",sheet_name="Experts") #change file path and sheet name
    list_of_records=df.to_dict(orient="records")

    for item in list_of_records:
        for field in item:
            if type(item[field])!=str:
                if math.isnan(item[field]):
                    item[field]=None
    print("POPULATING EXPERTS.................")
    for field in list_of_records:
        try:
            user = User.objects.get(Q(email=field['Email'])|Q(username=field['Expert Name']))
        except User.DoesNotExist:
            user = User.objects.create(username=field['Expert Name'],email=field['Email'])

        
        user_profile = UserProfile.objects.filter(user=user)
        if not field['One Liner']:
            desc = " "
        else:
            desc = field["One Liner"]
            print(desc)

        if not field['Functions of Expertise']:
            expertise = ""
        else:
            expertise= field["Functions of Expertise"]

        if not field['LinkedIn']:
            linkedin = ""
        else:
            linkedin = field['LinkedIn']

        if not field['Designation']:
            design = ""
        else:
            design = field['Designation']

        if not user_profile:

            user_profile=UserProfile.objects.create(
                user = user,
                role = 'Function Expert',
                google_email = field['Email'],
                name = field['Expert Name'],   
                company_name = field['Organisation'],   
                linkedin = linkedin,   
                profile_logo = field['Picture'],   
                description = desc,   
                sector_of_expertise = expertise,   
                domain_of_expertise = expertise,
                designation = design,

            )
            print(f"{user_profile.name} created")          


        else:
            user_profile.update(
                user = user,
                role = 'Function Expert',
                google_email = field['Email'],
                name = field['Expert Name'],   
                company_name = field['Organisation'],   
                linkedin = linkedin,   
                profile_logo = field['Picture'],   
                description = desc,   
                domain_of_expertise = expertise,
                sector_of_expertise = expertise,   
                designation = design,
                function_of_expertise = expertise,
                horizontals = field['Horizontals'],
                verticals = field['Verticals'],
                business_models = field['Business Model'],
            )  
            print(f"{user_profile[0].name} edited")          
