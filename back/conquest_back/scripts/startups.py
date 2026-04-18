from users.models import User,UserProfile,Startup,StartUpMember
from .coach import set_or_null 
import random
import pandas as pd
#############NOT COMPLETED#################

password_list=[]
def get_create_user(name:str):
    username=name.split(" ")[0]

    try:
        user=User.objects.get(username__contains=username)
        
    except:
        password=User.objects.make_random_password(length=10)
        user=User.objects.create_user(username=username+f"{random.randrange(100,999)}",
                                 password=password)
        entry={"Startup Name":name,
               'Username':user.username,
               'Password':password}
        password_list.append(entry)
        

        
    
    
    
    return user
def get_row(row):
    print(set_or_null(row['Co-Founder 1']),set_or_null(row['Co-Founder 2']),set_or_null(row['Co-Founder 3']))
    return {
        "startup_name":set_or_null(row['Startup Name']),
        "track":set_or_null(row['Track']),
        "website_url":set_or_null(row['Website']),
        "founder_name":set_or_null(row['Co-Founder 1']),
        "founder_linkedin":set_or_null(row['Co-Founder 1 LinkedIn']),
        "cofounder1_name":set_or_null(row['Co-Founder 2']),
        "cofounder1_linkedin":set_or_null(row['Co-Founder 2 LinkedIn']),
        "cofounder2_name":set_or_null(row['Co-Founder 3']),
        "cofounder2_linkedin":set_or_null(row['Co-Founder 3 LinkedIn']),
        "stage":set_or_null(row['Current Stage']),
        "description":set_or_null(row['General']),
        "problem_statement":set_or_null(row['Problem Statement']),
        "target_audience":set_or_null(row['Target Audience']),
        "revenue_stream":set_or_null(row['Revenue Stream']),
        "usp":set_or_null(row['USPs']),
        "competitors":set_or_null(row['Competitors']),
        "short_term_vision":set_or_null(row['Short Term Vision']),
        "long_term_vision":set_or_null(row['Long Term Vision']),
        "tam":set_or_null(row['TAM']),
        "sam":set_or_null(row['SAM']),
        "som":set_or_null(row['SOM']),
        "vertical":set_or_null(row['Vertical']),
        "horizontal":set_or_null(row['Horizontal']),
        "business_model":set_or_null(row['Business Model']),
        "fund_stage":set_or_null(row['Fund Stage']),
        "funding":set_or_null(row['Funding']),
        "valuation":set_or_null(row['Valuation']),

    }
def create_startup_member(startup:Startup,name,desig,linkedin):
        if name:
            member_edit=False
            try:
                member_edit=True
                member=StartUpMember.objects.get(under_startup=startup,
                                                name=name,)
            except:
                member=StartUpMember.objects.create(under_startup=startup,
                                                name=name,)
                
            if linkedin:
                member.linkedin=linkedin
            member.position=desig
            member.save()
            if member_edit:
                print(f"{member.name} edited")
            else:
                print(f"{member.name} created")

            return member

def create_startup_profile(user,data):
    edited=False
    try:
        startup_profile=Startup.objects.get(startup_name=data['startup_name'])
        edited=True
    except:
        user_profile=UserProfile.objects.create(name=data['startup_name'],
                                                user=user,
                                                role='Startup',
                                                website=data['website_url'])
        startup_profile=Startup.objects.create(user_profile=user_profile,startup_name=data['startup_name'])


        startup_profile.funding=data['funding']
        startup_profile.website_url=data['website_url'] or " "
        startup_profile.stage=data['stage']
        startup_profile.fund_stage=data['fund_stage']
        startup_profile.valuation=data['valuation']
        startup_profile.tam=data['tam']
        startup_profile.sam=data['sam']
        startup_profile.som=data['som']
        startup_profile.usp=data['usp']
        startup_profile.short_term_vision=data['short_term_vision']
        startup_profile.long_term_vision=data['long_term_vision']
        startup_profile.description=data['description'] or " "
        startup_profile.revenue_stream=data['revenue_stream']
        startup_profile.problem_statement=data['problem_statement']
        startup_profile.track=data['track']
        startup_profile.target_audience=data['target_audience']
        startup_profile.industry=data["vertical"]+","+data['business_model']
        startup_profile.functional_areas=data['horizontal']+","+data['business_model']
        startup_profile.competitors=data['competitors']
        startup_profile.location_hq=" "
        startup_profile.contact_email=' '
        startup_profile.team=' '
        startup_profile.save()
        print(f"making members of {startup_profile.startup_name}..........................")
        memeber1=create_startup_member(startup=startup_profile,
                                       name=data['founder_name'],
                                       desig='Founder',
                                       linkedin=data['founder_linkedin'])
        if data['cofounder1_name']:
            memeber2=create_startup_member(startup=startup_profile,
                                        name=data['cofounder1_name'],
                                        desig='Co-Founder 1',
                                        linkedin=data['cofounder1_linkedin'])
        if data['cofounder2_name']:
            memeber3=create_startup_member(startup=startup_profile,
                                        name=data['cofounder2_name'],
                                        desig='Co-Founder 2',
                                        linkedin=data['cofounder2_linkedin'])





    

    return startup_profile,edited

def run():
    df=pd.read_excel('scripts/Portal.xlsx',sheet_name='Startups',engine="openpyxl")
    print("##############################POPULATING STARTUPS##############################################")
    for index,row in df.iterrows():
        data=get_row(row)
        user=get_create_user(data['startup_name'])
        startup,edited=create_startup_profile(user,data)
        if edited:
            print(f"================={startup.startup_name} edited==================")
        else:
            print(f"================={startup.startup_name} created================")   
    print("making password file")
    df=pd.DataFrame.from_dict(password_list)
    df.to_excel('passwords.xlsx')
    print("password file created")


    







    