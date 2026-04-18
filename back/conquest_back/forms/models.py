from django.db import models
from users.models import UserProfile
# Create your models here.

class Form(models.Model):

    available_to=models.ManyToManyField(UserProfile)  
    form_name=models.CharField(max_length=100)
    def __str__(self) :
        return  f'{self.form_name}'


class SubjectiveQuestion(models.Model):

    type_choices = (
        ('Single Line','Single Line'),
        ('Short','Short'),
        ('Long','Long'),
    )
    form=models.ForeignKey(Form,on_delete=models.CASCADE,null=True,blank=True,related_name='subjective_questions')
    question=models.TextField()  #changed all questions from char to textfield
    type=models.CharField(max_length=11,choices=type_choices,default="Long")
    def __str__(self) :
        return  f'{self.question}'
    
    # class Meta:
    #     verbose_name=''
    #     verbose_name_plural=''

class FileUploadQuestion(models.Model):
    form=models.ForeignKey(Form,on_delete=models.CASCADE,null=True,blank=True,related_name='file_upload_questions')
    question=models.TextField()  #asking drive link for files
    def __str__(self) :
        return  f'{self.question}'

class ScoringQuestion(models.Model):
    form=models.ForeignKey(Form,on_delete=models.CASCADE,null=True,blank=True,related_name='scoring_questions')
    question=models.TextField()  #asking ans between 1 and 10
    def __str__(self) :
        return  f'{self.question}'


class PreferenceQuestion(models.Model):
    form=models.ForeignKey(Form,on_delete=models.CASCADE,related_name='preference_questions')
    question=models.TextField()  # rank its ranking_objs
    def __str__(self) :
        return  f'{self.question}'


class Preference(models.Model):
    under_question=models.ForeignKey(PreferenceQuestion,on_delete=models.CASCADE,null=True,blank=True,related_name='preferences')
    preference_name=models.TextField(null=True,blank=True)

    def __str__(self) :
        return  f'{self.preference_name}'


class Answer(models.Model):
    form=models.ForeignKey(Form,on_delete=models.CASCADE,related_name='answers')
    answered_by=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    def __str__(self) :
        return  f'{self.form.form_name}------{self.answered_by.user.username}'




class SubjectiveAns(models.Model):
    under_answer=models.ForeignKey(Answer,on_delete=models.CASCADE)
    subjective_question=models.ForeignKey(SubjectiveQuestion,on_delete=models.CASCADE)
    answer=models.TextField() 
    class Meta:
         verbose_name='Subjective Answer'
         verbose_name_plural='Subjective Answers'
    @property
    def question(self):
        return self.subjective_question.question


    def __str__(self) -> str:
        return f' {self.subjective_question.question}-------{self.answer}'

class ScoreAns(models.Model):
    under_answer=models.ForeignKey(Answer,on_delete=models.CASCADE)
    scoring_question=models.ForeignKey(ScoringQuestion,on_delete=models.CASCADE)
    answer=models.IntegerField(default=1) #max 10
    @property
    def question(self):
        return self.scoring_question.question
    def __str__(self) -> str:
        return f' {self.scoring_question.question}-------{self.answer}'
    class Meta:
         verbose_name='Scoring Answer'
         verbose_name_plural='Scoring Answers'

class  FileAns(models.Model):
    under_answer=models.ForeignKey(Answer,on_delete=models.CASCADE)
    file_question=models.ForeignKey(FileUploadQuestion,on_delete=models.CASCADE)
    answer=models.URLField() 
    @property
    def question(self):
        return self.file_question.question
    def __str__(self) -> str:
        return f' {self.file_question.question}-------{self.answer}'
    class Meta:
         verbose_name='Link'
         verbose_name_plural='Links'


class  PreferenceAnsMain(models.Model):
    
    under_answer=models.ForeignKey(Answer,on_delete=models.CASCADE)
    preference_question=models.ForeignKey(PreferenceQuestion,on_delete=models.CASCADE)
    #preference_order=models.ManyToManyField(Preference)
    @property
    def question(self):
        return self.preference_question.question
    @property
    def answer(self):
        ans=''
        for pref in self.preferenceans_set.all():
            ans+=f'{pref.preference}:{pref.position},'
        return ans
    def __str__(self) -> str:
        return f'{self.preference_question.question}'
    class Meta:
         verbose_name='Preference Question'
         verbose_name_plural='Preference Questions'

class PreferenceAns(models.Model):
    preference_ans=models.ForeignKey(PreferenceAnsMain,on_delete=models.CASCADE)
    preference_obj=models.ForeignKey(Preference,on_delete=models.CASCADE)
    position=models.IntegerField(default=0)
    @property
    def preference(self):
        return self.preference_obj.preference_name
    def __str__(self) -> str:
        return f'{self.preference_obj.preference_name}-------{self.position}'
   




























    


    