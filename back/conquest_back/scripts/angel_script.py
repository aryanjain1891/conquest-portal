import pandas as pd
import math
from users.models import UserProfile
from django.contrib.auth.models import User

def run():
    df = pd.read_excel("scripts/Portal.xlsx",sheet_name="Angels") #change file path and sheet name
    list_of_records=df.to_dict(orient="records")

    for item in list_of_records:
        for field in item:
            if type(item[field])!=str:
                if math.isnan(item[field]):
                    item[field]=None
    print("POPULATING ANGELS.........")
    for field in list_of_records:
        #field['Name']=field[' Name']
        try:
            email=field.get('Email',None)
            if email:
                user = User.objects.get(username=field['Name'])
                user.email=email
                user.save()
            else:
                user = User.objects.get(username=field['Name'])
        except User.DoesNotExist:
            user = User.objects.create(username=field['Name'])
            
        if email:        ##to add or change email if user only has username
            user.email=email
            user.save()

        user_profile = UserProfile.objects.filter(user=user)

        if not field['One Liner']:
                desc = " "
        else:
            desc = field["One Liner"]

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
                role = 'Angel',
                google_email = field.get('Email',None),
                name = field['Name'],   
                company_name = field['Organisation'],   
                linkedin = linkedin,   
                profile_logo = field['Picture'],   
                description = desc,   
                designation = design,
            )
            print(f"{user_profile.name} created")

        else:

            user_profile.update(
                user = user,
                role = 'Angel',
                google_email = field.get('Email',None),
                name = field['Name'],   
                company_name = field['Organisation'],   
                linkedin = linkedin,   
                profile_logo = field['Picture'],   
                description = desc,   
                designation = design,
            )
            print(f"{user_profile[0].name} edited")

            