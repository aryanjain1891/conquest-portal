from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
#emails
from django.core.mail import send_mail
from django.template.loader import render_to_string
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from users.models import UserProfile
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated


# Create your views here.

class GetForms(ListAPIView):
    permission_classes = [IsAuthenticated,]
    model = Form
    serializer_class = FormSerializer

    def get_queryset(self):
        user = self.request.user
        not_answered_forms=[]
        user_forms= Form.objects.filter(available_to__user=user)
        for form in user_forms:
            if not form.answers.filter(answered_by=user.profile):
                not_answered_forms.append(form)

        return not_answered_forms

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetFormQuestions(request,pk):
    try:
        form = Form.objects.get(id=pk)
        subjective_questions = form.subjective_questions.all()
        file_upload_questions = form.file_upload_questions.all()
        scoring_questions = form.scoring_questions.all()
        preference = []
        preference_questions = form.preference_questions.all()
        for i in preference_questions:
            preference_choice = i.preferences.all()
            serialized_preferences = PreferenceSerializer(preference_choice,many=True).data
            serialized_question=PreferenceQuestionSerializer(i).data
            serialized_question.update({'preferences':serialized_preferences})
            preference.append(serialized_question)
        response_json = {}
        response_json["form_id"]=pk
        response_json["form_name"]=form.form_name
        response_json["subjective_questions"]=SubjectiveQuestionSerializer(subjective_questions,many=True).data
        response_json["file_upload_questions"]=FileUploadQuestionSerializer(file_upload_questions,many=True).data
        response_json["scoring_questions"]=ScoringQuestionSerializer(scoring_questions,many=True).data
        response_json["preference_questions"]=preference
        return Response(response_json,status=200)
#{"subjective_questions":[{"question":"Subjective question 1"}],
# "file_upload_questions":[],"scoring_questions":[],
# "preference_questions":[{"question":"Preference question 1",
# "preferences":[{"preference_name":"Pre 1"},{"preference_name":"Pre 2"},{"preference_name":"Pre 3"}]}]}
    except Form.DoesNotExist:
        return Response({'error':'the form does not exist'},status=404)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def AddAnswers(request,pk):
    #{"subjective_questions":[{"question":question,"ans":ans},{},{}]}
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    try:
        form_answered = Form.objects.get(id=pk)
    except Form.DoesNotExist:
        return Response({"error":"form does not exist"},status=400)
    ans_obj = Answer.objects.create(form=form_answered,answered_by=user_profile)
    #get subjective questions and save their answers
    try:
        subjective_answers = request.data["subjective_questions"]
    except:
        return Response({'error':"subjective_questions key missing send empty list if no subj questions"},status=400)
    try:
        for ans in subjective_answers:
            try:
                try:
                    subjective_question_id = ans['id']
                    subjective_answer = ans['ans']
                except KeyError:
                    return Response({'error':'question id or answer is not provided'},status=400)
                question = SubjectiveQuestion.objects.get(id=subjective_question_id)
                # if question.type=='Single Line':
                #     if len(subjective_answer)<=200:
                #         SubjectiveAns.objects.create(under_answer=ans_obj,
                #                             subjective_question=question,
                #                             answer=subjective_answer)
                #     else:
                #         return Response({'error':'Single Line input answer too long'},status=400)
                # elif question.type=='Short':
                #     if len(subjective_answer)<=50:
                #         SubjectiveAns.objects.create(under_answer=ans_obj,
                #                             subjective_question=question,
                #                             answer=subjective_answer)
                #     else:
                #         return Response({'error':'Short input answer too long'},status=400)
                # elif question.type=='Long':
                SubjectiveAns.objects.create(under_answer=ans_obj,
                                    subjective_question=question,
                                    answer=subjective_answer)
            except SubjectiveQuestion.DoesNotExist :
                return Response({'error':'invalid question id'},status=400)
    except:
        return Response({'error':'subjective ans must be list'},status=400)




    #save answers for file upload questions
    try:
        file_upload_answers = request.data["file_upload_questions"]
    except:
        return Response({'error':"file_upload_questions key missing send empty list if no file questions"},status=400)
    try:
         for ans in file_upload_answers:
            try:
                try:
                    question_id = ans['id']
                    answer = ans['ans']
                except KeyError:
                    return Response({'error':'question id or answer is not provided'},status=400)
                question = FileUploadQuestion.objects.get(id=question_id)
                FileAns.objects.create(under_answer=ans_obj,
                                    file_question=question,
                                    answer=answer)
            except FileUploadQuestion.DoesNotExist:
                return Response({'error':'invalid question id'},status=400)
    except:
        return Response({'error':'file_upload_questions must be a list'},status=400)



    #save answers for scoring questions
    try:
        scoring_answers = request.data["scoring_questions"]
    except:
        return Response({'error':"scoring_questions key missing send empty list if no scoring questions"},status=400)
    try:  
        for ans in scoring_answers:
            try:
                try:
                    question_id = ans['id']
                    answer = ans['ans']
                except KeyError:
                    return Response({'error':'question id or answer is not provided'},status=400)
                if answer>10 or answer<=0:
                    return Response({'error':'score should be an integer from 1 to 10'},status=400)
                question = ScoringQuestion.objects.get(id=question_id)
                ScoreAns.objects.create(under_answer=ans_obj,
                                        scoring_question=question,
                                        answer=answer)
            except ScoringQuestion.DoesNotExist:
                return Response({'error':'invalid question id'},status=400)
    except:
        return Response({'error':"scoring_questions value must be a list"},status=400)


    #save answers for preference questions
    try:
        preference_answers = request.data["preference_questions"]
    except:
        return Response({'error':"preference_questions key missing send empty list if no preference questions"},status=400)

    try:
        for ans in preference_answers:
            try:
                try:
                    question_id = ans['id']
                    question = PreferenceQuestion.objects.get(id=question_id)
                    preference_ans = PreferenceAnsMain.objects.create(under_answer=ans_obj,
                                                                    preference_question=question)
                    no_of_preferences = len(ans["preferences"])
                except KeyError:
                    return Response({'error':'question id or preferences is not provided'},status=400)
                try:
                    for pref in ans["preferences"]:
                        ans_id = pref["id"]
                        preferece=Preference.objects.get(id=ans_id)
                        pos = pref["position"]
                        if pos<1 or pos>no_of_preferences:
                            return Response({'error':'invalid rank values'},status=400)
                        PreferenceAns.objects.create(preference_ans=preference_ans,
                                                    preference_obj=preferece,
                                                    position=pos)
                except:
                    return Response({"error":"preference must be a list of dicts"},status=400)
            except PreferenceQuestion.DoesNotExist:
                return Response({'error':'invalid question id'},status=400)
    except Exception as error :
        return Response({"error":f"{type(error).__name__}preference_questions value must be a list"},status=400)
    return Response({'success':'answers saved successfully'},status=200)



def get_email_content(resource_name, user_name):
    email_formats = {
        'Phionike123': {
            'subject': 'Phionike123 Benefits | Conquest BITS Pilani',
            'template': './emails/phionike123.html'
        },
        'MongoDB': {
            'subject': 'MongoDB Benefits | Conquest BITS Pilani',
            'template': './emails/mongodb.html'
        },
        'GitHub': {
            'subject': 'GitHub Benefits | Conquest BITS Pilani',
            'template': 'forms/github.html'
        },
        'WebFlow': {
            'subject': 'WebFlow Benefits | Conquest BITS Pilani',
            'template': './emails/webflow.html'
        },
        'SlydS': {
            'subject': 'SlydS Benefits | Conquest BITS Pilani',
            'template': './emails/slyds.html'
        },
        'Balsamiq': {
            'subject': 'Balsamiq Benefits | Conquest BITS Pilani',
            'template': './emails/balsamiq.html'
        },
        'DeckRooster': {
            'subject': 'DeckRooster Benefits | Conquest BITS Pilani',
            'template': './emails/deckrooster.html'
        },
        'Hackrew': {
            'subject': 'Hackrew Benefits | Conquest BITS Pilani',
            'template': './emails/hackrew.html'
        },
        'Auth0': {
            'subject': 'Auth0 Benefits | Conquest BITS Pilani',
            'template': './emails/auth0.html'
        },
        'DocSend': {
            'subject': 'DocSend Benefits | Conquest BITS Pilani',
            'template': './emails/docsend.html'
        },
        'Mixpanel': {
            'subject': 'Mixpanel Benefits | Conquest BITS Pilani',
            'template': './emails/mixpanel.html'
        },
        'HubSpot': {
            'subject': 'HubSpot Benefits | Conquest BITS Pilani',
            'template': './emails/hubspot.html'
        },
        'Stripe': {
            'subject': 'Stripe Benefits | Conquest BITS Pilani',
            'template': './emails/stripe.html'
        },
        'Notion': {
            'subject': 'Notion Benefits | Conquest BITS Pilani',
            'template': './emails/notion.html'
        },
        'Sprinto': {
            'subject': 'Sprinto Benefits | Conquest BITS Pilani',
            'template': './emails/sprinto.html'
        },
        'Tally': {
            'subject': 'Tally Benefits | Conquest BITS Pilani',
            'template': './emails/tally.html'
        },
        'CleverTap': {
            'subject': 'CleverTap Benefits | Conquest BITS Pilani',
            'template': './emails/clevertap.html'
        },
        'MathWorks': {
            'subject': 'MathWorks Benefits | Conquest BITS Pilani',
            'template': './emails/mathworks.html'
        },
        'Zoho': {
            'subject': 'Zoho Benefits | Conquest BITS Pilani',
            'template': './emails/zoho.html'
        },
    }

    if resource_name in email_formats:
        subject = email_formats[resource_name]['subject']
        template = email_formats[resource_name]['template']
    else:
        subject = f'{resource_name} Benefits | Conquest BITS Pilani'
        template = 'emails/default.html'

    message = render_to_string(template, {'user_name': user_name, 'resource_name': resource_name})
    return subject, message



@api_view(["GET","POST"])
@permission_classes([IsAuthenticated])
def send_resource_email(request):

    #return Response({"message":"feature not configured yet"},status=200) #THIS IS A TEMPORARY LINE PLEASE COMMENT WHEN COMPLETED
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        return Response({'status': 'error', 'message': 'User profile not found'}, status=404)

    if user_profile.role != "Startup":
        return Response({'status': 'error', 'message': 'User not a startup'}, status=403)

    if request.method == 'POST':
        if not request.user.email:
            return Response({"error":"user has no email"},status=400)
        try:
            data = request.data
            print(data)
            resource_name = data['user'].get('username').strip('')
            print("===>", resource_name)
            #resource_name = data.get('resource_name', '').strip()
            sender_email = settings.DEFAULT_FROM_EMAIL
            recipient_email = request.user.email
            user_name = user_profile.name

            subject, message = get_email_content(resource_name, user_name)

            send_mail(
                subject,
                message,
                sender_email,
                [recipient_email],
                fail_silently=False,
                html_message=message,
            )

            return Response({'status': 'success', 'message': 'Email sent successfully'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=400)
    else:
        return Response({'status': 'error', 'message': 'Invalid request method'}, status=405)
        


            
