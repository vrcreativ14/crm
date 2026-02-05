from django.shortcuts import render
from healthinsurance_shared.models import *
from healthinsurance.models.quote import *
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from healthinsurance.models.quote import MAF, Quote, Order
from healthinsurance.models.deal import Deal
import json
#import pymupdf

def index(request, *args, **kwargs):
    return render(request, 'frontendHealthinsuranceQuote/index.html')


def QuestionsForm(request, id):
    deal_id = id
    d = Deal.objects.filter(pk = deal_id)
    quote = Quote.objects.filter(deal = d[0]) if d.exists() else ''
    deal = quote[0].deal if quote else None
    # primary_member = deal.primary_member
    insurer = 'Cigna'
    provider = Insurer.objects.filter(name = 'Cigna')
    questions = ''
    applicant_questions = ''
    arr = {}
    j = {}
    if provider:
            medical_questions = Question.objects.filter(insurers = provider[0], categories__category__name='Medical')
            # for q in questions:
            #      if q.answers:
            #         a = q.answers.split(',')
            #         q.answers = a
            applicant_questions = Question.objects.filter(insurers = provider[0], categories__name='Applicant Details').order_by('priority')
            application_questions = Question.objects.filter(insurers = provider[0], categories__name='Application Details')
    if quote.exists():
        quote = quote[0]
        maf = MAF.objects.filter(quote = quote)
        if maf.exists():
            arr = maf[0].qna_json
            arr['saved'] = True
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
    }
    return render(request, 'frontendHealthinsuranceQuote/cigna.html', context)


@csrf_exempt
def MafApi(request, id): 
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
                insurer = 'Cigna'
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


