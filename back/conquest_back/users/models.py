from django.db import models
from django.db.models import Q

from django.contrib.auth.models import  User, Group, AbstractUser, Permission
from django.conf import settings
from django.core.exceptions import ValidationError


# Create your models here.

ALL_ROLES = (
    ('Mentor', 'Mentor'),
    ('Function Expert', 'Function Expert'),
    ('Coach', 'Coach'),
    ('Startup', 'Startup'),
    ('Partner - Company', 'Partner - Company'),
    ('Partner - Individual Connected', 'Partner - Individual Connected'),
    ('Community', 'Community'),
    ('Alumni', 'Alumni'),
    ('Guest - Tier 1', 'Guest - Tier 1'),
    ('Guest - Tier 2', 'Guest - Tier 2'),
    ('CEL Admin', 'CEL Admin'),
    ('DVM Admin', 'DVM Admin'),
    ('Angel','Angel'),
    ('Consultant','Consultant')

)
CAN_VIEW={
    "Partner - Company":('Mentor','Function Expert','Coach','Partner - Company','Community','Partner - Individual Connected','Angel','Consultant'),
    "Community":('Mentor','Function Expert','Coach','Partner - Company','Community','Alumni','Partner - Individual Connected','Angel','Consultant'),
    "Alumni":('Partner - Company','Partner - Individual Connected'),
    "Guest - Tier 1":('Mentor','Function Expert','Coach','Partner - Company','Community','Alumni','Startup','Partner - Individual Connected','Angel','Consultant'),
    "Guest - Tier 2":('Startup'),
    "Partner - Individual Connected":('Mentor','Function Expert','Coach','Partner - Company','Community','Partner - Individual Connected','Angel','Consultant'),

}
CAN_REQUEST={
    "Startup":('Startup','Partner - Company','Community','Alumni','Partner - Individual Connected')
}
CAN_CREATE={
    "Partner - Company":('Startup','Alumni'),
    "Startup":('Mentor','Function Expert','Coach','Angel','Consultant'),
    "Partner - Individual Connected":('Startup','Alumni'),
    "Community":('Startup'),
    "Alumni":('Mentor','Function Expert','Coach','Startup','Community','Alumni','Angel'),
    "Mentor":('Mentor','Function Expert','Coach','Partner - Company','Community','Alumni','Partner - Individual Connected','Angel','Consultant'),
    "Angel":('Mentor','Function Expert','Coach','Partner - Company','Community','Alumni','Partner - Individual Connected','Angel','Consultant'),
    "Function Expert":('Mentor','Function Expert','Coach','Partner - Company','Community','Alumni','Partner - Individual Connected','Angel','Consultant'),
    "Coach":('Mentor','Function Expert','Coach','Partner - Company','Community','Alumni','Partner - Individual Connected','Angel','Consultant'),
    "Consultant":('Mentor','Function Expert','Coach','Partner - Company','Community','Alumni','Partner - Individual Connected','Angel','Consultant'),

    
}
TYPE_OF_PARTNER = (
    ('Corporate','Corporate') ,
    ('Investment','Investment') ,
    ('Outreach','Outreach') ,
    ('Ecosystem','Ecosystem') ,
    ('Knowledge','Knowledge') ,
    ('Community','Community') ,
    )

def try_appender(array,dict,key):


    try:
        to_append=dict[key]
    except KeyError:
        return array
    #print(to_append)
    
    #new_list=array+list(to_append)
    #print (new_list)
    return array+list(to_append)
    

    

class UserProfile(models.Model):
    #basic info for all authenticated users
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
    # phone_number = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(max_length=50, choices=ALL_ROLES)
    profile_logo = models.URLField( null=True, blank=True,max_length=500)
    google_email = models.EmailField(null=True,blank=True)
    google_user_id = models.CharField(null=True,blank=True,max_length=200)

    #coach mentor specific field
    name=models.CharField(max_length=50,null=True,blank=True)
    company_name=models.CharField(max_length=200,null=True,blank=True)
    designation = models.CharField(max_length=200, blank=True)
    linkedin = models.URLField(blank=True,max_length=500)
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True,null=True)
    resume = models.URLField( null=True, blank=True,max_length=500)
    sector_of_expertise = models.CharField(max_length=200, blank=True ,null=True)
    domain_of_expertise = models.CharField(max_length=200, blank=True ,null=True)
    type_of_partner = models.CharField(max_length=20,choices=TYPE_OF_PARTNER,blank=True,null=True)
    website = models.URLField(null=True,blank=True,max_length=500)
    verticals = models.CharField(null=True,blank=True,max_length=255)
    horizontals = models.CharField(null=True,blank=True,max_length=255)
    business_models = models.CharField(null=True,blank=True,max_length=255)
    function_of_expertise = models.CharField(null=True,blank=True,max_length=255)
    offering=models.TextField(null=True,blank=True)
    data_complete=models.BooleanField(default=False)
    no_of_calls=models.CharField(default=" ")
    comments=models.TextField(null=True,blank=True)
    # groups = models.ManyToManyField(Group, verbose_name=('groups'), blank=True,related_name='user_groups') #group like cel group; guest tier etc.
    def __str__(self):
        return f'{self.name}---{self.role}'
    
    def can_view(self):
        queryset=[]
        
        if self.role in list(CAN_VIEW.keys()) or self.role in list(CAN_CREATE.keys()) or self.role in list(CAN_REQUEST.keys()):
            can_view=[]
            can_view=try_appender(can_view,CAN_VIEW,self.role)
            #print(can_view)
            can_view=try_appender(can_view,CAN_CREATE,self.role)
            #print(can_view)
            can_view=try_appender(can_view,CAN_REQUEST,self.role)
            can_view_users=UserProfile.objects.select_related('user').filter(role__in=can_view)
            queryset = can_view_users.exclude(pk=self.pk)

        return queryset

    def can_create(self):
        queryset=[]

        if self.role in list(CAN_CREATE.keys()):
            can_create=[]
            can_create=try_appender(can_create,CAN_CREATE,self.role)
            can_create_users=UserProfile.objects.select_related('user').filter(role__in=can_create)
            queryset=can_create_users.exclude(pk=self.pk)
            # for user in can_create_users:
            #     if user.role in can_create:
            #         queryset.append(user)
            
        return queryset
        
    def can_request(self):
        queryset=[]

        if self.role in list(CAN_REQUEST.keys()):
            can_request=[]
            can_request=try_appender(can_request,CAN_REQUEST,self.role)
            can_request_users=UserProfile.objects.select_related("user").filter(role__in=can_request)
            queryset=can_request_users.exclude(pk=self.pk)
            # for user in can_request_users:
            #     if user.role in can_request:
            #         queryset.append(user)
            
        return queryset
    
   

class Startup(models.Model):
    user_profile=models.OneToOneField(UserProfile,on_delete=models.SET_NULL,null=True,blank=True) #to connnect startup to user
    startup_name = models.CharField(max_length=255)
    profile_logo = models.URLField( null=True, blank=True,max_length=500)
    description = models.TextField()
    stage = models.CharField(max_length=100)
    industry = models.CharField(max_length=200,null=True,blank=True)
    functional_areas = models.CharField(max_length=200,null=True,blank=True)
    location_hq = models.CharField(max_length=100,null=True,blank=True)
    pitch_deck = models.URLField( null=True, blank=True,max_length=500)
    linkedin = models.URLField(blank=True,max_length=500)
    twitter=models.URLField(null=True,blank=True,max_length=500)
    contact_email = models.EmailField(null=True,blank=True)
    website_url = models.URLField(blank=True,max_length=500)
    video_pitch = models.URLField( null=True, blank=True,max_length=500)
    team = models.CharField(max_length=100,null=True,blank=True)
    investors=models.CharField(max_length=255,null=True,blank=True)
    track=models.CharField(max_length=255,null=True,blank=True)
    problem_statement=models.TextField(blank=True,null=True)
    target_audience=models.TextField(blank=True,null=True)
    revenue_stream=models.TextField(blank=True,null=True)
    usp=models.TextField(blank=True,null=True)
    short_term_vision=models.TextField(blank=True,null=True)
    long_term_vision=models.TextField(blank=True,null=True)
    competitors=models.TextField(blank=True,null=True)
    tam=models.CharField(max_length=255,null=True,blank=True)
    sam =models.CharField(max_length=255,null=True,blank=True)
    som=models.CharField(max_length=255,null=True,blank=True)
    funding =models.CharField(max_length=255,null=True,blank=True)
    fund_stage =models.CharField(max_length=255,null=True,blank=True)
    valuation=models.CharField(max_length=255,null=True,blank=True)
    #foreign keys
    startup_champion = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='championed_startups_assigned')
    startup_poc = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='poc_startups_assigned')
    #m2m
    data_complete=models.BooleanField(default=False)
    registration_steps_completed=models.IntegerField(default=0)
    under_guidance_of = models.ManyToManyField(UserProfile,  related_name='guided_startups', blank=True)
    def __str__(self):
        return self.startup_name
    
class Connection(models.Model):
    from_user=models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name='sent_connections')
    to_user=models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name='recieved_connections')
    approved=models.BooleanField(default=False)
    accepted=models.BooleanField(default=False)

    def __str__(self) :
        return f'from:{self.from_user} | to:{self.to_user}'

    def clean(self):
        if self.from_user == self.to_user:
            raise ValidationError("Connection cannot be made to the same user.")
        
        existing_connections = Connection.objects.filter(
            models.Q(from_user=self.from_user, to_user=self.to_user) | 
            models.Q(from_user=self.to_user, to_user=self.from_user)
        )
        
        # Exclude the current instance if it exists
        if self.pk:
            existing_connections = existing_connections.exclude(pk=self.pk)
        
        if existing_connections.exists():
            raise ValidationError("This connection request already exists.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class StartUpMember(models.Model):
    position=models.CharField(max_length=100)
    name=models.CharField(max_length=100)
    linkedin=models.URLField()
    profile_pic=models.URLField(null=True,blank=True)
    under_startup=models.ForeignKey(Startup,on_delete=models.CASCADE,related_name='team_members')

    def __str__(self) -> str:
        return f'{self.position}----{self.name}----{self.under_startup.startup_name}'
    
class InterestCapture(models.Model):
    from_startup = models.ForeignKey(Startup, on_delete=models.CASCADE)
    for_consultant = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={"role": "Consultant"}, null=True, blank=True, related_name='consultant_interests')
    for_resource = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={"role": "Partner - Company"}, null=True, blank=True, related_name='resource_interests')
    interest_captured = models.BooleanField(default=True)

    def __str__(self):
        if self.for_consultant:
            return f'{self.from_startup}----{self.for_consultant.name}--consultant'
        elif self.for_resource:
            return f'{self.from_startup}----{self.for_resource.user.username}--resource'
        return f'{self.from_startup}----Unknown'
