from .coach import set_or_null,get_user,edit_create_profile
import pandas as pd



def get_row(row):
        try:
          coach_name=set_or_null(row["Name"])
        except:
          coach_name=set_or_null(row[" Name"])
        coach_email=set_or_null(row.get('Email',None))
        coach_desig=set_or_null(row["Designation"])
        coach_org=set_or_null(row["Organisation"] )
        coach_linkedin=set_or_null(row['LinkedIn'] )
        try:
            coach_pic=set_or_null(row['Picture'])
        except:
             coach_pic=set_or_null(row['Logo'])
        coach_des=set_or_null(row['One Liner']) or ""
        coach_exp=set_or_null(row.get('Sectors of Interest',None))
        website=set_or_null(row.get('Website',None))
        return {
             "name":coach_name,
             "email":coach_email,
             "designation":coach_desig,
             "company_name":coach_org,
             "linkedin":coach_linkedin,
             "profile_logo":coach_pic,
             "description":coach_des,
             "sector_of_expertise":coach_exp,
             "website":website
            }


def run():

    ####INVESTMENT PARTNERS########################
    df=pd.read_excel("scripts/Portal.xlsx",engine='openpyxl',sheet_name='Investment Partners')
    # print(df.head()["Organisation"])
    print("=========================POPULATING INVESTMENT PARTNERS================================")
    for index,row in df.iterrows():
         partner_data=get_row(row)
         user=get_user(partner_data["email"],partner_data["name"])
         partner_profile,edited=edit_create_profile(user,partner_data,"Partner - Individual Connected")
         if not edited:
           print(f"{partner_profile.name} created")
           partner_profile.type_of_partner='Investment'
           partner_profile.save()
         else:
                partner_profile.designation=partner_data['designation'] 
                partner_profile.save()

                print(f"{partner_profile.name} edited")

    ####INVESTMENT PARTNERS########################

    ####KNOWLEDGE PARTNERS########################
    print("=========================POPULATING KNOWLEDGE PARTNERS================================")


    df=pd.read_excel("scripts/Portal.xlsx",engine='openpyxl',sheet_name='Knowledge Partners')
    for index,row in df.iterrows():
         partner_data=get_row(row)
         user=get_user(partner_data["email"],partner_data["name"])
         partner_profile,edited=edit_create_profile(user,partner_data,"Partner - Individual Connected")
         if not edited:
           print(f"{partner_profile.name} created")
           partner_profile.type_of_partner='Knowledge'
           partner_profile.save()
         else:
                partner_profile.designation=partner_data['designation'] 
                partner_profile.save()
                
                print(f"{partner_profile.name} edited")
    ####KNOWLEDGE PARTNERS########################



    ####COMMUNITY PARTNERS########################
    print("=========================POPULATING COMMUNITY PARTNERS================================")


    df=pd.read_excel("scripts/Portal.xlsx",engine='openpyxl',sheet_name='Community Partner')
    for index,row in df.iterrows():
         partner_data=get_row(row)
         user=get_user(partner_data["email"],partner_data["name"])
         partner_profile,edited=edit_create_profile(user,partner_data,"Partner - Individual Connected")
         if not edited:
           print(f"{partner_profile.name} created")
           partner_profile.type_of_partner='Community'
           partner_profile.save()
         else:
                partner_profile.designation=partner_data['designation'] 
                partner_profile.save()

                
                print(f"{partner_profile.name} edited")

    ####Community PARTNERS########################

    ####Corportate PARTNERS########################
    print("=========================POPULATING CORPORATE PARTNERS================================")


    df=pd.read_excel("scripts/Portal.xlsx",engine='openpyxl',sheet_name='Corporate Partners')
    for index,row in df.iterrows():
         partner_data=get_row(row)
         user=get_user(partner_data["email"],partner_data["name"])
         partner_profile,edited=edit_create_profile(user,partner_data,"Partner - Individual Connected")
         if not edited:
           print(f"{partner_profile.name} created")
           partner_profile.type_of_partner='Corporate'
           partner_profile.save()
         else:
                partner_profile.designation=partner_data['designation'] 
                partner_profile.save()

                
                print(f"{partner_profile.name} edited")
    
    


        
    
    

    



