from import_export import resources,fields,widgets
from .models import *
from import_export.forms import ImportForm

class AnswerResource(resources.ModelResource):
    form__form_name=fields.Field("form__form_name",column_name='Form name')
    answered_by = fields.Field(
        column_name='Answered By',
        attribute='answered_by',
        widget=widgets.ForeignKeyWidget(UserProfile,'name') #name
    )

    subjectiveans_set=fields.Field('subjectiveans_set',
                                   column_name="Subjective Answers",
                                   widget=widgets.ManyToManyWidget(SubjectiveAns,field='answer',
                                                                   separator="||"),
                                                                   m2m_add=True
                                                                   )
    scoreans_set=fields.Field('scoreans_set',
                                   column_name="Integer answers",
                                   widget=widgets.ManyToManyWidget(ScoreAns,field='answer',
                                                                   separator="||"),
                                                                   )
    fileans_set=fields.Field('fileans_set',
                                   column_name="File links",
                                   widget=widgets.ManyToManyWidget(FileAns,field='answer',
                                                                   separator="||",),
                                                                   )
    
    preferenceansmain_set=fields.Field('preferenceansmain_set',
                                   column_name="Preference Answers",
                                   widget=widgets.ManyToManyWidget(PreferenceAnsMain,field='answer',
                                                                   separator="||"),
                                                                   )
    # pref_ans=fields.Field(column_name='Pref Answers',
    #                       attribute='pref_ans')
                

    class Meta:
        model=Answer
        fields=("id","form__form_name","answered_by","subjectiveans_set","scoreans_set","fileans_set",'preferenceansmain_set')





