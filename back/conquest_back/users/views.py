from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import User, UserProfile, Startup, Connection, ALL_ROLES,InterestCapture
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
import random
import requests
from rest_framework.permissions import AllowAny
from rest_framework.authentication import authenticate
import datetime
from django.db.models import Q
from django.conf import settings
from .utils import upload_photo
from pathlib import Path
from django.contrib.auth.models import User


# Create your views here.
def get_token_for_user(user):

    tokens = RefreshToken.for_user(user)
    return tokens


## signup, signin, update, googleOauth,


class GoogleLogout(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            if not refresh_token:
                return Response(
                    {"error": "refresh_token not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except KeyError:
            return Response(
                {"error": "invalid request format"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GoogleLogin(APIView):
    def post(self, request):

        try:

            access_token = request.data.get("access_token")  # name to be updated
            # print(access_token)
        except Exception:
            return Response({"error": "invalid request format"})

        profile_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        profile_info_response = requests.get(profile_info_url, headers=headers)
        # print(profile_info_response)

        if profile_info_response.ok:
            profile_info_response = profile_info_response.json()

            email = profile_info_response["email"]
            user = User.objects.filter(email=email).first()

            if user:
                user_profile=user.profile

                tokens = get_token_for_user(
                    user
                )  # check if refresh token is working, prev token blacklisted

                if user_profile.data_complete or user_profile.role == "Guest - Tier 2":

                    return Response(
                        {
                            "message": "user verified and data complete",
                            "tokens": {
                                "refresh": str(tokens),
                                "access": str(tokens.access_token),
                                "access_token_lifetime": settings.ACCESS_TOKEN_LIFETIME.total_seconds() * 1000,
                                'refresh_token_lifetime': settings.REFRESH_TOKEN_LIFETIME.total_seconds() * 1000,
                            },
                            "user_profile_obj": UserProfileSerializer(
                                user_profile
                            ).data,
                            "user_pfp_url": profile_info_response["picture"],
                        },
                        status=200,
                    )
                else:
                    serialized_user_profile = UserProfileSerializer(user_profile)
                    return Response(
                        {
                            "message": "user verified but data incomplete",
                            "user_obj":UserSerializer(user).data,
                            "user_profile_obj": serialized_user_profile.data,
                            "user_pfp_url": profile_info_response["picture"],
                            "tokens": {
                                "refresh": str(tokens),
                                "access": str(tokens.access_token),
                                "access_token_lifetime": settings.ACCESS_TOKEN_LIFETIME.total_seconds() * 1000,
                                'refresh_token_lifetime': settings.REFRESH_TOKEN_LIFETIME.total_seconds() * 1000,
                            },
                        },
                        status=200,
                    )
            else:
                # new user from google
                google_user_id = profile_info_response["id"]
                new_user = User.objects.create(
                    username=google_user_id,
                    email=profile_info_response["email"],
                )
                new_user_profile = UserProfile.objects.create(  #to add name if it is included in oauth scope
                    user=new_user,
                    role="Guest - Tier 2",  # default role
                    google_email=email,
                    google_user_id=google_user_id,
                )
                tokens = get_token_for_user(new_user)

                return Response(
                    {
                        "message": "new guest user created",
                        "user_obj": UserSerializer(new_user).data,
                        "user_profile_obj": UserProfileSerializer(
                            new_user_profile
                        ).data,
                        "user_pfp_url": profile_info_response["picture"],
                        "tokens": {
                            "refresh": str(tokens),
                            "access": str(tokens.access_token),
                            "access_token_lifetime": settings.ACCESS_TOKEN_LIFETIME.total_seconds() * 1000,
                            'refresh_token_lifetime': settings.REFRESH_TOKEN_LIFETIME.total_seconds() * 1000,
                        },
                    },
                    status=200,
                )
        else:
            return Response({"error": "invalid token"}, status=400)


class UsernameLogin(APIView):
    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            if not username or not password:
                return Response({"message": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(username=username, password=password)
            if user is None:
                return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                user_profile=user.profile
                user_startup_profile = user.profile.startup
            except AttributeError:
                return Response({"message": "Startup profile doesn't exist. Contact administrator."}, status=status.HTTP_404_NOT_FOUND)

            tokens = get_token_for_user(user)
            profile_serializer = UserProfileSerializer(user_profile).data
            startup_serializer = StartupSerializer(user_startup_profile).data

            return Response({
                "message": "Startup user logged in successfully.",
                "tokens": {
                    "refresh": str(tokens),
                    "access": str(tokens.access_token),
                    "access_token_lifetime": settings.ACCESS_TOKEN_LIFETIME.total_seconds() * 1000,
                    'refresh_token_lifetime': settings.REFRESH_TOKEN_LIFETIME.total_seconds() * 1000,
                },
                "success": "true",
                "user_profile_obj": profile_serializer,
                "startup_profile": startup_serializer
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class RegisterProfileView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     # parser_classes = [MultiPartParser]
#     def post(self, request):
#         try:
#             # user image?
#             user_username = request.data["username"]
#             user_password = request.data["password"]
#             user_email = request.data["email"]
#             user_designation = request.data["designation"]
#             user_linkedin = request.data["linkedin"]
#             user_location = request.data["location"]
#             user_sector = request.data["sector_of_expertise"]
#             user_domain = request.data["domain_of_expertise"]
#             # =====Add or remove fields as necessary====#
#         except KeyError:
#             return Response({"error": "invalid request format"}, status=400)

#         request.user.update(username=user_username, password=user_password)
#         try:

#             UserProfile.objects.filter(user=request.user).update(
#                 contact_email=user_email,
#                 designation=user_designation,
#                 linkedin=user_linkedin,
#                 location=user_location,
#                 sector_of_expertise=user_sector,
#                 domain_of_expertise=user_domain,
#                 data_complete=True,
#                 # add or remove fields as neccessary
#             )
#         except UserProfile.DoesNotExist:
#             return Response({"error": "user has no profile "})

#         if request.user.userprofile.role == "Startup":

#             return Response(
#                 {
#                     "message": "registration incomplete redirect to startup registration form"
#                 }
#             )
#         else:
#             return Response({"message": "registration complete"})


# class RegisterStartupView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     # parser_classes = [MultiPartParser]

#     def post(self, request):

#         try:

#             startup_field = request.data["startup_field"]
#             # =====Add or remove fields as necessary====#
#         except KeyError:
#             return Response({"error": "invalid request format"})

#         if request.user.userprofile.role == "Startup":
#             new_startup = Startup.objects.create(
#                 user=request.user.userprofile,
#                 ##to be complete when registration form is final
#             )

#             # ====this endpoint will be recalled after each step of registration====#
#             ##to be complete when registration form is final

#             return Response(
#                 {
#                     "message": "registration complete",
#                     "startup_obj": StartupSerializer(new_startup).data,
#                 },
#                 status=200,
#             )
#         else:
#             return Response({"error": "not a startup"}, status=403)




#================DIRECTORY ENDPOINTS=====================#
#returns list of all startups
class StartupListView(APIView):

    permission_classes=[IsAuthenticated] 

    def get(self,request):

        startups=Startup.objects.select_related("user_profile",'user_profile__user',).prefetch_related("team_members").all()
        serialized_startups_data=StartupSerializer(startups,many=True).data

        return Response({'startup_list':serialized_startups_data},status=200)
    
#returns list of all experts
class ExpertListView(APIView):
    permission_classes=[IsAuthenticated] #not sure if required


    def get(self,request):
        experts=UserProfile.objects.select_related("user").filter(role='Function Expert')
        mentors=UserProfile.objects.select_related("user").filter(role='Mentor')
        coaches=UserProfile.objects.select_related("user").filter(role='Coach')
        resource_partners=UserProfile.objects.select_related("user").filter(role='Partner - Company')
        investment_partners=UserProfile.objects.select_related("user").filter(role='Partner - Individual Connected')


        serialized_experts_data=UserProfileSerializer(experts,many=True).data
        serialized_mentor_data=UserProfileSerializer(mentors,many=True).data
        serialized_coach_data=UserProfileSerializer(coaches,many=True).data
        serialized_resource_partners_data=UserProfileSerializer(resource_partners,many=True).data
        serialized_investment_partners_data=UserProfileSerializer(investment_partners,many=True).data

        return Response({'expert_list':serialized_experts_data,
                         'mentor_list':serialized_mentor_data,
                         'coach_list':serialized_coach_data,
                         "resource_partners":serialized_resource_partners_data,
                         "investment_partners":serialized_investment_partners_data},status=200)
    
class StartupDetailView(APIView):
    permission_classes=[IsAuthenticated] 
    def get(self,request):
        try:
            startup_id=int(request.GET['id'])
            if not isinstance(startup_id,int):
             return Response({"error":"id must be int"},status=400)
        except:
             return Response({"error":"startup id missing"},status=400)
        try:
            req_startup=Startup.objects.get(id=startup_id)
        except:
             return Response({"error":"startup not found"},status=404)
        

        from_conn= Connection.objects.filter(from_user=request.user.profile,to_user=req_startup.user_profile) 
        to_conn= Connection.objects.filter(from_user=req_startup.user_profile,to_user=request.user.profile)
        connection=''
        if from_conn or to_conn:
            if to_conn:
                if to_conn.first().approved:
                    connection='received'    #connection request received by user to be accepted or declined
                    if to_conn.first().accepted:
                        connection='connected'
                else:
                    connection='not-connected'  ##connection not approved yet so not sent to user
            
            if from_conn:
                if not from_conn.first().accepted:
                    connection='sent'   ##connection was sent to the user
                else:
                    connection='connected'

            
        else:
            connection='not-connected'
            
        
        
        
        serialized_startup_data=StartupDetailSerializer(req_startup).data
        serialized_startup_data['connection']=connection
        return Response(serialized_startup_data,status=200)
    
class UserProfileDetailView(APIView):
    permission_classes=[IsAuthenticated] 
    def get(self,request):
        try:
            profile_id=int(request.GET['id'])
            if not isinstance(profile_id,int):
             return Response({"error":"id must be int"},status=400)
        except:
             return Response({"error":"profile id missing"},status=400)
        try:
            req_profile=UserProfile.objects.get(id=profile_id)
        except:
             return Response({"error":"profile not found"},status=404)
        
        from_conn= Connection.objects.filter(from_user=request.user.profile,to_user=req_profile) 
        to_conn= Connection.objects.filter(from_user=req_profile,to_user=request.user.profile)
        connection=''
        if from_conn or to_conn:
            if to_conn:
                if to_conn.first().approved:
                    connection='received'    #connection request received by user to be accepted or declined
                    if to_conn.first().accepted:
                        connection='connected'
                else:
                    connection='not-connected'  ##connection not approved yet so not sent to user
            
            if from_conn:
                if not from_conn.first().accepted:
                    connection='sent'   ##connection was sent to the user
                else:
                    connection='connected'

            
        else:
            connection='not-connected'
            
            


            
        
        serialized_profile_data=UserProfileSerializer(req_profile).data
        serialized_profile_data['connection']=connection
        return Response(serialized_profile_data,status=200)


        


            


    
                         
    
#returns all startups under a cme 
class StartupsUnderMentorView(APIView):
    
    permission_classes=[IsAuthenticated] 

    def get(self,request):
        CME=['Mentor','Function Expert','Coach']
        try:
            #mentor_name=request.data['username']
            mentor_id=int(request.GET['id'])
            if not isinstance(mentor_id,int):
             return Response({"error":"id must be int"},status=400)
        except:
            return Response({"error":"invalid request format"},status=400)
    
        try:
            mentor_obj= UserProfile.objects.get(id=mentor_id)
            if mentor_obj.role not in CME:
                return Response({"error":"user not a guider"},status=400)
        except:
            return Response({"error":"mentor not found"},
                            status=status.HTTP_404_NOT_FOUND)
        
        guided_startups=mentor_obj.guided_startups.all() 
        #if len(guided_startups)==0:
       #     return Response({"message":"this mentor has no startups under him yet"},status=200) 
        serialized_startup_data=StartupSerializer(guided_startups,many=True).data

        return Response({"guided_startups":serialized_startup_data},status=200)
    
#================DIRECTORY ENDPOINTS===================#

#================Connection ENDPOINTS===================#

class ListConnections(APIView):

    permission_classes=[IsAuthenticated]

    def get(self,request):
        try:
            user_profile=request.user.profile
        except:
            return Response({"error":"user has no user profile"},
                            status=404)
        
        connections_accepted=Connection.objects.filter(Q(from_user=user_profile)|Q(to_user=user_profile)).filter(accepted=True)
        connected_user_profiles=[]
        for connection in connections_accepted:
            if connection.from_user==user_profile:
                user_data = UserProfileSerializer(connection.to_user).data
                connected_user_profiles.append({"user": user_data, "connection_id": connection.id})
            else:
                user_data = UserProfileSerializer(connection.from_user).data
                connected_user_profiles.append({"user": user_data, "connection_id": connection.id})
        
        connections_unaccepted_sent=Connection.objects.filter(from_user=user_profile).filter(Q(accepted=False))
        connection_unaccepted_recieved=Connection.objects.filter(to_user=user_profile).filter(Q(accepted=False)&Q(approved=True))
        ###connection will only be recieved by the to_user after being approved by CEL admin
        serialized_accepted_connections=ConnectionSerializer(connections_accepted,many=True).data
        serialized_pending_connections=ConnectionSerializer(connections_unaccepted_sent,many=True).data
        serialized_waiting_connections=ConnectionSerializer(connection_unaccepted_recieved,many=True).data

        return Response({"connected_users":connected_user_profiles,
                         "connections_accepted":serialized_accepted_connections,
                         "connections_unaccepted_sent":serialized_pending_connections,
                         "connection_unaccepted_recieved":serialized_waiting_connections},status=200)
    


class SendConnectionView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            to_user_username=request.data['username']
        except KeyError:
            return Response({"error":"invalid request format", "connection": None},status=400)

        try:
            to_user=UserProfile.objects.get(user__username=to_user_username)
        except:
            return Response({"error":"user does not exist", "connection": None},status=404)
        
        if to_user==request.user:
            return Response({"error":"cannot send connection request to self", "connection": None},status=400)

        if to_user not in request.user.profile.can_view():
            return Response({"error":"permission denied", "connection": None},status=403)
        
        if Connection.objects.filter(to_user=to_user, from_user=request.user.profile).exists() or Connection.objects.filter(to_user=request.user.profile, from_user=to_user).exists():
            return Response({"error": "This connection already exists.", "connection": None}, status=400)
        
        connection=Connection.objects.create(from_user=request.user.profile,
                                             to_user=to_user)
        
        serialized_connection = ConnectionSerializer(connection).data
        
        return Response({"message":"connection created succesfully", "connection": serialized_connection},status=201)
    

class AcceptConnectionView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            connection_status=request.data['status']
            connection_id=request.data['id']
            if not isinstance(connection_status,bool) or not isinstance(connection_id,int):
                return Response({"error":"connection id int and status bool"},status=400)
        except KeyError:
            return Response({"error":"invalid request format"},status=400)
        
        try:
            connection=Connection.objects.get(id=connection_id)
        except:
            return Response({"error":"connection not found"},status=400)
        
        if not connection.approved:
            return Response({"error":"connection not approved yet"},status=403)
        
        if not connection_status:
            connection.delete()
            return Response({"message":"connection successfully denied"},status=204)
        
        connection.accepted=True
        connection.save()
        return Response({"message":"connection successfully accepeted"},status=200)

class DeleteConnectionView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            connection_id=int(request.data['id'])
            if not isinstance(connection_id, int):
                return Response({"error":"connection id int"}, status=400)
        except KeyError:
            return Response({"error":"invalid request format"}, status=400)
        
        try:
            connection = Connection.objects.get(id=connection_id)
        except:
            return Response({"error":"connection not found"},status=400)
        
        connection.delete()
        return Response({"message": "connection succesfully deleted"}, status=200)
    
#================Connection ENDPOINTS===================#


class SearchProfile(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            query=request.GET.get('query')  #query here is an url parameter /search/?query=query
        except:
            query=None

        can_view_users=request.user.profile.can_view()
        if query and can_view_users:
            query_set=can_view_users.select_related("user").filter(Q(name__icontains=query)|
                                                    Q(description__icontains=query)|
                                                    Q(location__icontains=query)|
                                                    Q(sector_of_expertise__icontains=query)|
                                                    Q(domain_of_expertise__icontains=query)|
                                                    Q(company_name__icontains=query)
                                                    )
            serialized_queryset=UserProfileSerializer(query_set,many=True).data
            return Response({'user_profiles':serialized_queryset},status=200)
        return Response({'user_profiles':UserProfileSerializer(can_view_users,many=True).data},status=200)
        
####################Profile Endpoints#############################

class RetrieveEditProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_profile = UserProfile.objects.get(user= request.user)
            serialized_user = UserProfileSerializer(user_profile)
            return Response(serialized_user.data,status=200)
        except UserProfile.DoesNotExist:
            return Response({'error':'Profile Does Not Exist.'},status=401)
    
    def put(self,request):
        #this endpoint takes in all editable fields and updates only those fields whose values have been supplied
        fields={}
        try:
                profile_logo=request.data['profile_logo']
                user_username=request.data['user']['username']
                user_password=request.data['user']['password']
                user_fname=request.data['user']['first_name']
                user_lname=request.data['user']['last_name']
                fields["description"]=request.data['description']
                fields["resume"]=request.data['resume']
                fields["google_email"]=request.data['google_email']
                fields["designation"]=request.data['designation'] #
                fields["linkedin"]=request.data['linkedin']
                fields["location"]=request.data['location']  #
                fields["sector_of_expertise"]=request.data['sector_of_expertise'] #
                fields["domain_of_expertise"]=request.data['domain_of_expertise'] #
                fields["company_name"]=request.data['company_name']  #
                
        except KeyError:
            return Response({"error":"invalid request format"},status=400)

        user = request.user
        if user_username!="":user.usernmae = user_username
        if user_password!="":user.set_password(user_password)
        if fields['google_email']!="":user.email = fields["google_email"]
        if user_fname!="":user.first_name = user_fname
        if user_lname!="":user.last_name = user_lname
        user.save()

        if user_fname=="" and user_lname!="":user_fname = request.user.first_name
        if user_lname=="" and user_fname!="":user_lname = request.user.last_name
        user_name = user_fname+" "+user_lname
        fields["name"]=user_name

        if profile_logo!="":
            profile_logo,filename=upload_photo(profile_logo,request.user.username)
            Path.unlink(f"/home/app/web/{filename}")
            fields["profile_logo"]=profile_logo

        #error checks
        for field in ["designation","location","company_name"]:
            if len(fields[field])>100:
                return Response({"error":f"{field} cannot be more than 100 characters long"},status=400)
        
        for field in ["sector_of_expertise","domain_of_expertise"]:
            if len(fields[field])>200:
                return Response({"error":f"{field} cannot be more than 200 characters long"},status=400)

        if len(fields["name"])>50:
            return Response({"error":"name cannot be more than 50 characters long"},status=400)
            
        #this part removes the fields which shouldn't be updated
        fields_to_not_update = []
        for field in fields:
            if fields[field]=="":
                fields_to_not_update.append(field)
        for field in fields_to_not_update:
            del fields[field]

        if fields["name"]==" ":
            del fields["name"]

        try:

            UserProfile.objects.filter(user=request.user).update(**fields)
            return Response({'success':'data has been successfully updates'},status=200)
        except UserProfile.DoesNotExist:
            return Response({'error':'user has no profile '},status=401)
        
class RetrieveEditStartupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            startup_profile = Startup.objects.get(user_profile__user = request.user)
            if startup_profile.user_profile.role != "Startup":
                return Response({'error':'Current user is not a startup.Please use the profile endpoint.'},status=400)
            else:
                try:
                    startup_champion = startup_profile.startup_champion.user.get_full_name()
                except AttributeError:
                    startup_champion = None
                try:
                    startup_poc = startup_profile.startup_champion.user.get_full_name()
                except AttributeError:
                    startup_poc = None
                startup = startup_profile.startup_name
                coach_mentor_expert = startup_profile.under_guidance_of.all()
                coach,mentor,expert=None,None,None
                for i in coach_mentor_expert:
                    if i.role=='Coach':
                        coach = i.user.get_full_name()
                    elif i.role == 'Mentor':
                        mentor = i.user.get_full_name()
                    elif i.role == 'Function Expert':
                        expert = i.user.get_full_name()
                startup = {
                            "startup_champion":startup_champion,
                           "startup_poc" : startup_poc,
                           "coach":coach,
                           "mentor":mentor,
                           "expert":expert
                           }
                serialized_startup = StartupSerializer(startup_profile)
                startup.update(serialized_startup.data)
                return Response(startup,status=200)
        except Startup.DoesNotExist:
            return Response({'error':'Startup Does Not Exist.'},status=400)
    
    def put(self,request):
        fields = {}
        try:
                fields["startup_name"]=request.data['startup_name']#255
                profile_logo=request.data['profile_logo']
                Startup_username=request.data['user_profile']['user']['username']
                Startup_password=request.data['user_profile']['user']['password']
                Startup_fname=request.data['user_profile']['user']['first_name']
                Startup_lname=request.data['user_profile']['user']['last_name']
                fields["description"]=request.data["description"]
                fields["stage"]=request.data["stage"]#
                fields["contact_email"]=request.data['contact_email']
                fields["industry"]=request.data['industry']##
                fields["pitch_deck"]=request.data['pitch_deck']
                fields["location_hq"]=request.data['location_hq']#
                fields["linkedin"]=request.data['linkedin']
                fields["website_url"]=request.data['website_url']
                fields["video_pitch"]=request.data['video_pitch']
                fields["team"]=request.data['team']#
                fields["twitter"]=request.data['twitter']
                fields["functional_areas"]=request.data['functional_areas']##
                fields["short_term_vision"]=request.data['short_term_vision']

        except KeyError:
            return Response({"error":"invalid request format"},status=400)

        user = request.user
        if Startup_username!="":user.username = Startup_username
        if Startup_password!="":user.set_password(Startup_password) 
        if fields["contact_email"]!="":user.email = fields["contact_email"]
        if Startup_fname!="":user.first_name = Startup_fname
        if Startup_lname!="":user.last_name = Startup_lname
        user.save()

        if profile_logo!="":
            profile_logo,filename=upload_photo(profile_logo,request.user.username)
            Path.unlink(f"/home/app/web/{filename}")
            fields["profile_logo"]=profile_logo

        #error checks
        for field in ["location_hq","team","stage"]:
            if len(fields[field])>100:
                return Response({"error":f"{field} cannot be more than 100 characters long"},status=400)
        
        for field in ["industry","functional_areas"]:
            if len(fields[field])>200:
                return Response({"error":f"{field} cannot be more than 200 characters long"},status=400)
            
        if len(fields["startup_name"])>255:
            return Response({"error":"startup name cannot be more than 255 characters long"},status=400)
            
        #this part removes the fields which shouldn't be updated
        fields_to_not_update = []
        for field in fields:
            if fields[field]=="":
                fields_to_not_update.append(field)
        for field in fields_to_not_update:
            del fields[field]

        try:

            Startup.objects.filter(user_profile__user = request.user).update(**fields)
            return Response({'success':'data has been successfully updated'},status=200)
            
        except Startup.DoesNotExist:
            return Response({'error':'startup has no profile '},status=400) 

class UpdateEmail(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            userprofile = request.user.profile
            email = request.data["email"]
            
            if not email=="":
                if userprofile.role=="Startup":
                    startup = Startup.objects.get(user_profile=userprofile)
                    startup.contact_email = email
                    startup.save()
                userprofile.google_email = email
                userprofile.save()
                return Response({"success":"email has been successfully updated."},status=200)
        except UserProfile.DoesNotExist:
            return Response({'error':'User Profile does not exist.'},status=404)
        except KeyError:
            return Response({'error':'invalid request format.'},status=400)

####################RoleWise User Lists Endpoints#############################

class RoleList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            role = request.GET['role']
        except:
            return Response({"error": 'role not specified'}, status=400)
        roles = [r[0] for r in ALL_ROLES]
        if role not in roles:
            return Response({"error": "not a valid role"}, status=400)
        
        can_view_users=request.user.profile.can_view()
        queryset = can_view_users.filter(role=role)
        serialized_queryset = UserProfileSerializer(queryset, many=True).data
        return Response({"list": serialized_queryset}, status=200)

class InterestCaptureView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            requested_name = request.data['name']
            requested_type = request.data['type']
            
            startup_profile = request.user.profile.startup
            
            if requested_type == "consultant":
                target = UserProfile.objects.filter(name=requested_name, role="Consultant").first()
                if not target:
                    return Response({"error": "No consultant found with that name"}, status=404)
                obj, created = InterestCapture.objects.get_or_create(
                    from_startup=startup_profile,
                    for_consultant=target
                )
                target_display = f"{target.name}--consultant"
            elif requested_type == "resource":
                target = UserProfile.objects.filter(
                    company_name=requested_name,
                    role="Partner - Company"
                ).first()
                if not target:
                    return Response({"error": "No resource found with that company_name"}, status=404)
                obj, created = InterestCapture.objects.get_or_create(
                    from_startup=startup_profile,
                    for_resource=target
                )
                target_display = f"{target.user.username}--resource"
            else:
                return Response({"error": "Invalid type"}, status=400)
            
            return Response({
                "message": "Interest was captured successfully" if created else "Interest was already captured",
                "interest_status": obj.interest_captured,
                "target": target_display
            }, status=201 if created else 200)
            
        except AttributeError:
            return Response({"error": "User is not associated with a startup"}, status=403)
        except KeyError:
            return Response({"error": "Missing required fields"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
