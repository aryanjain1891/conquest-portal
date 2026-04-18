from collections.abc import Callable, Sequence
from typing import Any
from django.contrib import admin
from django.http import HttpRequest
from .models import *
from django.forms.widgets import CheckboxSelectMultiple,TextInput,Textarea
from nested_inline.admin import NestedModelAdmin,NestedStackedInline,NestedTabularInline
from import_export.admin import ExportActionMixin,ImportExportModelAdmin
from .resources import AnswerResource
# Register your models here.

#django-nested-inline enables inlining models with those who are already inlined
#==============FORM MODEL REGISTERED==============#
class SubjectiveQuesAdmin(NestedStackedInline):
    model=SubjectiveQuestion
    extra=1
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={
            'rows': 5,
            'cols': 70,
            'style': 'resize: both;',
            #'onkeydown': "if (event.key === 'Enter' && event.target.tagName.toLowerCase() === 'textarea') {event.preventDefault();}"

        })},
    }
class ScoreQuesAdmin(NestedStackedInline):
    model=ScoringQuestion
    extra=1
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={
            'rows': 5,
            'cols': 70,
            'style': 'resize: both;',
            #'onkeydown': "if (event.key === 'Enter' && event.target.tagName.toLowerCase() === 'textarea') {event.preventDefault();}"

        })},
    }
class FileQuesAdmin(NestedStackedInline):
    model=FileUploadQuestion
    extra=1
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={
            'rows': 5,
            'cols': 70,
            'style': 'resize: both;',
            #'onkeydown': "if (event.key === 'Enter' && event.target.tagName.toLowerCase() === 'textarea') {event.preventDefault();}"

        })},
    }
class PreferenceAdmin(NestedTabularInline):
    model=Preference
    fk_name='under_question'
    extra=2
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={
            'rows': 5,
            'cols': 40,
            'style': 'resize: both;',
            #'onkeydown': "if (event.key === 'Enter' && event.target.tagName.toLowerCase() === 'textarea') {event.preventDefault();}"

        })},
    }
class PreferenceQuesAdmin(NestedStackedInline,):
    inlines=[PreferenceAdmin]
    model=PreferenceQuestion
    extra=1
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={
            'rows': 5,
            'cols': 70,
            'style': 'resize: both;',
            #'onkeydown': "if (event.key === 'Enter' && event.target.tagName.toLowerCase() === 'textarea') {event.preventDefault();}"
        })},
    } 

class FormAdmin(NestedModelAdmin):
    inlines=[SubjectiveQuesAdmin,ScoreQuesAdmin,FileQuesAdmin,PreferenceQuesAdmin]
    model=Form
    list_display = ('form_name','answered_by')
    search_fields = ('form_name',)
    filter_horizontal = ('available_to',)  
    def answered_by(self,obj):
        return len(obj.answers.all())
    def has_view_permission(self,request,obj=None):
        if request.user.is_superuser or request.user.is_staff: #only cel admin and dvm admin can view
            return True
            
        
        # try:
        #     profile=request.user.profile #UNCOMMENT IF CEL ADMIN IS NOT STAFF USER
        #     if profile.role=="CEL ADMIN":
        #         return True
        #     else:
        #         return False
        # except:
        #     return False
admin.site.register(Form,FormAdmin)#change this in case of custom AdminSite
#==============FORM MODEL REGISTERED==============#
##ASSUMING CEL ADMIN WILL BE STAFF USER###
#==============ANSWER MODEL REGISTERED==============#
#made ans readonly so they cant be changed
#Answers are readonly for cel admin and editable for dvm admin#
class AnswerPermissions:
    def has_delete_permission(self,request,obj):
        return request.user.is_superuser
    
    def has_add_permission(self,request,obj):
        return request.user.is_superuser
    
    def get_readonly_fields(self, request: HttpRequest, obj: Any | None = ...) -> list[str] | tuple[Any, ...]:
        if not request.user.is_superuser:
            return self.readonly_fields
        else:
            return ()
    def get_fields(self, request: HttpRequest, obj: Any | None = ...) -> Sequence[Callable[..., Any] | str]:
        if not request.user.is_superuser:
            return self.fields  ###these are fields editable by cel admin
        elif request.user.is_superuser:
            return self.all_fields ###these are fields editable by dvm admin only
        else: 
            return ()

    
    
    
class SubjAnsAdmin(AnswerPermissions,NestedStackedInline):
    model=SubjectiveAns
    fields=('question','answer')
    readonly_fields=('question',)
    all_fields=('subjective_question','answer')         
    extra=0
    #this function makes answer field readonly for cel admin and editable for dvm
    ##while maintaing resizable widget
    def formfield_for_dbfield(self, db_field, request, **kwargs):  
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'answer':
            if not request.user.is_superuser:
                formfield.widget = Textarea(attrs={
                'rows': 5,
                'cols': 70,
                'readonly': 'readonly',
                'style': 'resize: both;'
            })
            else:
                formfield.widget = Textarea(attrs={
                'rows': 5,
                'cols': 70,
                'style': 'resize: both;'
            })

        return formfield
   
    
class ScoreAnsAdmin(AnswerPermissions,NestedStackedInline):
    model=ScoreAns         
    fields=('question','answer')
    readonly_fields=('question','answer')
    all_fields=('scoring_question','answer')         
    extra=0
   
class FileAnsAdmin(AnswerPermissions,NestedStackedInline):
    model=FileAns      
    fields=('question','answer')
    readonly_fields=('question','answer')
    all_fields=('file_question','answer')         
    extra=0
    
class PreferenceAnsAdmin(AnswerPermissions,NestedStackedInline):
    model=PreferenceAns
    all_fields=('preference_obj','position')         
    fields=('preference','position')
    readonly_fields=('preference','position')
    #extra=0
    sortable_by=('position',)
    fk_name='preference_ans'
    def get_extra(self,request,obj,**kwargs):
        if not request.user.is_superuser:
            return 0
        return 1
    
class PreferenceMainAnsAdmin(AnswerPermissions,NestedStackedInline):
    model=PreferenceAnsMain
    all_fields=('preference_question',)         
    fields=('question',)   
    readonly_fields=('question',)
    #extra=0
    inlines=[PreferenceAnsAdmin]
    def get_extra(self,request,obj,**kwargs):
        if not request.user.is_superuser:
            return 0
        return 1
   
class AnswerAdmin(NestedModelAdmin,ImportExportModelAdmin,ExportActionMixin):
    model=Answer
    list_display=('form','answered_by')
    resource_class=AnswerResource
    list_per_page=50
    list_filter=('form',)
    #list_select_related=('form','answered_by')
    search_fields = ('form__form_name','answered_by__user__username')
    readonly_fields=('answered_by',)
    inlines=[SubjAnsAdmin,ScoreAnsAdmin,FileAnsAdmin,PreferenceMainAnsAdmin]
    def get_readonly_fields(self,request,obj=None):
        if request.user.is_superuser:
            return []
        return self.readonly_fields
    def has_delete_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:
        return request.user.is_superuser
    def has_add_permission(self, request):
        return request.user.is_superuser
    def has_view_permission(self,request,obj=None):
        if request.user.is_superuser or request.user.is_staff:  #only cel admin and dvm admin can view
            return True
        
        # try:                              #UNCOMMENT IF CEL ADMIN IS NOT STAFF USER
        #     profile=request.user.profile
        #     if profile.role=="CEL ADMIN":
        #         return True
        #     else:
        #         return False
        # except:

        #     return False
    def get_export_filename(self, request, queryset, file_format):
        return queryset[0].form.form_name+'-Answers'
    

admin.site.register(Answer,AnswerAdmin) #change this in case of custom AdminSite
#==============ANSWER MODEL REGISTERED==============#


