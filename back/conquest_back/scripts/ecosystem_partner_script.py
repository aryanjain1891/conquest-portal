import pandas as pd
import math
from users.models import UserProfile
from django.contrib.auth.models import User

def run():

    df = pd.read_excel("scripts/Portal.xlsx",sheet_name="Ecosystem Partners") #change file path and sheet name
    list_of_records=df.to_dict(orient="records")

    for item in list_of_records:
        for field in item:
            if type(item[field])!=str:
                if math.isnan(item[field]):
                    item[field]=None
    print("Populating Ecosystem partners..............")
    for field in list_of_records:
        #field['Name']=field[' Name']
        field['Sectors of Interest']=None
        field['Portfolio']=None
        try:
            email=field.get('Email',None)
            if email:
                user = User.objects.get(email=field.get('Email',None))
            else:
                user = User.objects.get(username=field['Name'])
        except User.DoesNotExist:
            user = User.objects.create(username=field['Name'])
        if email:
                user.email=email
                user.save()


        
        user_profile = UserProfile.objects.filter(user=user)
        if field['Partner Title']=="Investment Partner":
            role = "Investment"
        elif field['Partner Title']=="Outreach Partner":
            role = "Outreach"
        elif field['Partner Title']=="Ecosystem Partner":
            role = "Ecosystem"
        if not user_profile:
            if not field['One Liner']:
                desc = " "
            else:
                desc = field["One Liner"]

            if not field['Sectors of Interest']:
                expertise = ""
            else:
                expertise= field["Sectors of Interest"]
                
            if not field['Designation']:
                design = ""
            else:
                design = field['Designation']

            user_profile=UserProfile.objects.create(
                user = user,
                role = "Partner - Individual Connected",
                google_email = field.get('Email',None),
                name = field['Name'],   
                company_name = field['Organisation'],   
                profile_logo = field['Picture'],   
                description = desc,   
                sector_of_expertise = expertise,   
                domain_of_expertise = expertise,
                linkedin="",
                designation = design,
                type_of_partner = role,
                website = field["Website"]
            )
            print(f"{user_profile.name} created")

        else:
            user_profile.update(
                user = user,
                role = "Partner - Individual Connected",
                google_email = field.get('Email',None),
                name = field['Name'],   
                company_name = field['Organisation'],   
                linkedin ="",   
                profile_logo = field['Picture'],   
                description = field['One Liner' ],   
                sector_of_expertise = field['Sectors of Interest'],   
                domain_of_expertise = field['Sectors of Interest'],
                resume = field['Portfolio'],
                designation = field['Designation'],
                type_of_partner = role,
            )
            print(f"{user_profile[0].name} edited")

            