from django.shortcuts import render, redirect
from healthinsurance_shared.models import *
from healthinsurance.models.quote import *
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from healthinsurance.models.quote import MAF, Quote, Order
from healthinsurance.models.deal import Deal
import logging
import json
import pymupdf

api_logger = logging.getLogger("api.amplitude")

def index(request, *args, **kwargs):
    return render(request, 'frontendHealthinsuranceQuote/index.html')


def QuestionsForm(request, secretKey, id, str):
    stages = ['applicants_details', 'medical_details', 'application_details']
    members = ['primary']
    current_stage = ''
    current_member = ''
    try:
            deal_id = id
            d = Deal.objects.filter(pk = deal_id)
            quote = Quote.objects.filter(deal = d[0]) if d.exists() else ''
            quote_id = quote[0].id if quote.exists() else None
            deal = quote[0].deal if quote.exists() else None
            # primary_member = deal.primary_member
            insurer = 'Cigna'
            order = Order.objects.filter(deal = d[0]) if d.exists() else None
            provider = order[0].selected_plan.plan.insurer if order.exists() else None
            # provider = Insurer.objects.filter(name__icontains = 'Cigna')
            questions = ''
            applicant_questions = ''
            arr = {}
            j = {}
            for m in deal.primary_member.additional_members.all():
                 members.append(m.pk)
            if provider:
                    medical_questions = Question.objects.filter(insurers = provider, categories__category__name='Medical')
                    # for q in questions:
                    #      if q.answers:
                    #         a = q.answers.split(',')
                    #         q.answers = a
                    applicant_questions = Question.objects.filter(insurers = provider, categories__name='Applicant Details').order_by('priority')
                    application_questions = Question.objects.filter(insurers = provider, categories__name='Application Details')
                    if quote.exists():
                        quote = quote[0]
                        maf = MAF.objects.filter(quote = quote)
                        if maf.exists():
                            arr = maf[0].qna_json
                            arr['saved'] = True
                            for key,value in arr.items():
                                if not isinstance(value, dict):
                                    continue
                                # for key, value in arr[k]:
                                #      count = count + 1
                                stages.remove(key)
                                if len(arr[key]) < len(members):
                                     current_stage = key
                                else:
                                     current_stage = stages[0]
                            if current_stage in arr:
                                for k,v in arr[current_stage].items():
                                    members.remove(k)
                                current_member = members[0]
                            else:
                                current_member = 'primary'
                                      
                                     

                                
                                
                                     
                        else:            
                                for q in questions:
                                    j = {}
                                    print(q)
                                    j['qid'] = q.pk
                                    j['type'] = q.answer_form
                                    j['answer'] = False if q.answer_form == 'B' else ''
                                    rq_arr = []
                                    for rq in q.related_questions.all():                                
                                        rq_dict = {}
                                    #j['rq']['']
                                        for qn in rq.qna.all():
                                            #j[q.pk][rq.pk][qn.pk] = []
                                            rq_dict['rqid'] = qn.pk
                                            rq_dict['text'] = qn.question
                                            rq_dict['type'] = qn.answer_type
                                            rq_dict['answer'] = False if qn.answer_type == 'B' else ''
                                            rq_arr.append(rq_dict)
                                            rq_dict = {}
                                    
                                        j['rq'] = rq_arr
                                    arr[q.pk] = j
                                arr['saved'] = False
                            #arr.append(j)
                            # else:
                            #     print('questions' + questions)
                        
                        context = {
                            'medical_questions' : medical_questions,
                            'applicant_questions' : applicant_questions,
                            'application_questions' : application_questions,
                            'deal' : deal,
                            'json' : arr,
                            'current_stage': current_stage,
                            'current_member': current_member,
                        }
                        return render(request, 'frontendHealthinsuranceQuote/cigna.html', context)

                    else:
                         pass
            else:
                 return redirect('/health-insurance-quote/{}/{}'.format(secretKey,id))

                 #return JsonResponse({'success':False, 'message': 'Provider does not exists'})
    
    except Exception as e:
            api_logger.error('Error in MAF form {}'.format(e))
            return JsonResponse({'success': False, 'message': 'Could not retreive data for this MAF'})
    


@csrf_exempt
def MafApi(request, id):
    try:
        deal_id = id
        d = Deal.objects.filter(pk = deal_id)
        quote = Quote.objects.filter(deal = d[0]) if d.exists() else ''
        quote = quote[0] if quote.exists() else None
        # deal = quote.deal if quote else None
        arr = {}
        maf = MAF.objects.filter(quote = quote) if quote else None
        if request.method == 'GET':
            if maf and maf.exists():
                    maf = maf[0]
                    #o.selected_plan.plan.insurer.name
                    j = maf.qna_json
                    arr = j
                    arr['saved'] = True
                    pass
                
            else:
                    # primary_member = deal.primary_member
                    # insurer = 'Cigna'
                    provider = Insurer.objects.filter(name = 'Cigna')
                    questions = ''
                    j = {}
                    if provider:
                        questions = Question.objects.filter(insurers = provider[0])
                        for q in questions:
                            j = {}
                            print(q)
                            j['qid'] = q.pk
                            j['type'] = q.answer_form
                            j['answer'] = False if q.answer_form == 'B' else ''
                            rq_arr = {}
                            for rq in q.related_questions.all():                                
                                rq_dict = {}
                                #j['rq']['']
                                for qn in rq.qna.all():
                                    #j[q.pk][rq.pk][qn.pk] = []
                                    rq_dict['rqid'] = qn.pk
                                    rq_dict['text'] = qn.question
                                    rq_dict['type'] = qn.answer_type
                                    rq_dict['answer'] = False if qn.answer_type == 'B' else ''
                                    rq_arr[qn.pk] = rq_dict
                                    rq_dict = {}
                                
                                j['rq'] = rq_arr
                            arr[q.pk] = j

                        #arr.append(j)
                        arr['saved'] = False
                    else:
                        print('questions' + questions)



            return JsonResponse(arr, safe=False)

        elif request.method == 'POST':
            print(request)
            j = json.loads(request.POST.get('data'))
            j['saved'] = True
            if maf.exists():
                maf = maf[0]
                saved_data = maf.qna_json
                for key, value in j.items():
                    #saved_data[key] = [saved_data[key], j[key]]
                    if not isinstance(value, dict):
                        continue
                    for k,v in j[key].items():
                        saved_data[key][k] = j[key][k]
                    pass
                
                maf.qna_json = saved_data
                maf.save()
            else:
                # quote = quote[0] if quote.exists() else None
                if quote and j:
                    MAF.objects.create(quote = quote, qna_json = j)
                pass

            return HttpResponse('Data Saved Successfully')
        
    except Exception as e:
        api_logger.error('Error in MAF form {}'.format(e))
        return JsonResponse({'success': False, 'message': 'Could not get/post data for this MAF'})


def DocumentPDF(quote_id):
     quote = Quote.objects.filter(pk = quote_id)
     maf = MAF.objects.filter(quote = quote[0]) if quote.exists() else None
     maf = maf[0] if maf.exists() else None
     if maf and quote:
     #  doc=pymupdf.open("C:/Users/asus/Downloads/CIGNA MEDICAL APPLICATION FORM.pdf")
        j = maf.qna_json
        applicant_details = j['applicant_details']
        medical_details = j['medical_details']
        application_details = j['application_details']
        if applicant_details:
             pass
        doc=pymupdf.open("C:/Users/asus/proj/nexus/CIGNA_MEDICAL_APPLICATION_FORM____.pdf")
        p = 0
        w = 0
        for page in doc:
            print(page)
            for w in page.widgets():
                print('{} -- {} -- {} -- {} -- {} -- {}'.format(w.field_name, w.field_label, w.field_type_string, w.field_value, w.choice_values ,w.button_states()))
     
        return HttpResponse('pdf')
     
     else:
          return "Quote doesn't exists"
     
