from django.shortcuts import render, redirect
from django.conf import settings
from healthinsurance_shared.models import *
from healthinsurance.models.quote import *
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from healthinsurance.models.quote import MAF, Quote, Order
from healthinsurance.models.deal import Deal
from io import BytesIO
import logging
import json
import fitz
import requests




api_logger = logging.getLogger("api.amplitude")

form_stages_integer = {
     1:'applicants_details',
     2:'medical_details',
     3:'application_details',
}

form_stages = {
     'applicants_details':1,
     'medical_details':2,
     'application_details':3,
}

def get_next_stage_integer(stage_str):
     try:
        return form_stages_integer[form_stages[stage_str] + 1]
     except:
        return 'applicants_details'


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
            insurer = 'Cigna'
            order = Order.objects.filter(deal = d[0]) if d.exists() else None
            provider = order[0].selected_plan.plan.insurer if order.exists() else None
            questions = ''
            applicant_questions = ''
            arr = {}
            j = {}
            for m in deal.primary_member.additional_members.all():
                 members.append(m.pk)
            if provider:
                    medical_questions = Question.objects.filter(insurers = provider, categories__category__name='Medical')
                    applicant_questions = Question.objects.filter(insurers = provider, categories__name='Applicant Details').order_by('priority')
                    application_questions = Question.objects.filter(insurers = provider, categories__name='Application Details')
                    if quote.exists():
                        quote = quote[0]
                        maf = MAF.objects.filter(quote = quote)
                        if maf.exists():
                            arr = maf[0].qna_json
                            arr['saved'] = True
                            current_stage = arr['current_stage']
                            for key,value in arr.items():
                                if not isinstance(value, dict):
                                    continue
                                
                            if current_stage == 'applicants_details':
                                 current_member = int(arr['current_member'])         
                                     
                        else:   
                                current_stage = 'applicants_details'
                                current_member = 'primary'        
                                for q in questions:
                                    j = {}
                                    print(q)
                                    j['qid'] = q.pk
                                    j['type'] = q.answer_form
                                    j['answer'] = False if q.answer_form == 'B' else ''
                                    rq_arr = []
                                    for rq in q.related_questions.all():                                
                                        rq_dict = {}
                                    
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
    
    except Exception as e:
            api_logger.error('Error in MAF form {}'.format(e))
            return JsonResponse({'success': False, 'message': 'Could not retreive data for this MAF'})
    


@csrf_exempt
def MafApi(request, id):
    try:
        deal_id = id
        d = Deal.objects.filter(pk = deal_id)
        deal = d[0] if d.exists() else None
        quote = Quote.objects.filter(deal = deal) if deal else None
        quote = quote[0] if quote.exists() else None
        # deal = quote.deal if quote else None
        arr = {}
        answer_json = {}
        maf = MAF.objects.filter(quote = quote) if quote else None
        if request.method == 'GET':
            if maf and maf.exists():
                    maf = maf[0]
                    #o.selected_plan.plan.insurer.name
                    j = maf.qna_json
                    arr = j
                    arr['saved'] = True
                    answer_json = arr
                    pass
                
            else:
                    # primary_member = deal.primary_member
                    # insurer = 'Cigna'
                    order = Order.objects.filter(deal = d[0]) if d.exists() else None
                    provider = order[0].selected_plan.plan.insurer if order.exists() else None
                    # provider = Insurer.objects.filter(name = 'Cigna')
                    answer_json['saved'] = False
                    answer_json['applicants_details'] = {}
                    answer_json['medical_details'] = {}
                    answer_json['application_details'] = {}
                    medical_questions = Question.objects.filter(insurers = provider, categories__category__name__icontains='medical')
                    applicant_questions = Question.objects.filter(insurers = provider, categories__name__icontains='applicant details').order_by('priority')
                    application_questions = Question.objects.filter(insurers = provider, categories__name__icontains='application details')

                    answer_json['applicants_details']['primary'] = {}
                    for q in applicant_questions:
                            answer_json['applicants_details']['primary'][q.text] = ''
                            for rq in q.related_questions.all():
                                 answer_json['applicants_details']['primary'][q.text] = {'rq':{rq.pk:''}}
                                #answer_json['applicants_details']['primary'][q.text]['rq'][rq.pk]['answer'] = ''
                        
                    answer_json['medical_details']['primary'] = {}
                    for q in medical_questions:
                            answer_json['medical_details']['primary'][q.pk] = ''
                            for rq in q.related_questions.all():
                                 answer_json['medical_details']['primary'][q.pk] = {'rq':{rq.pk:''}}
                        
                    
                    answer_json['application_details']['primary'] = {}
                    for q in application_questions:
                            answer_json['application_details']['primary'][q.pk] = ''
                            for rq in q.related_questions.all():
                                 answer_json['application_details']['primary'][q.pk] = {'rq':{rq.pk:''}}
                                 

                    # for k,v in answer_json.items():
                    for member in deal.primary_member.additional_members.all():
                        answer_json['applicants_details'][member.pk] = {}
                        for q in applicant_questions:                            
                            answer_json['applicants_details'][member.pk][q.pk] = ''
                            for rq in q.related_questions.all():
                                 answer_json['applicants_details'][member.pk][q.pk] = {'rq':{rq.pk:''}}
                                 


                        answer_json['medical_details'][member.pk] = {}
                        for q in medical_questions:                            
                            answer_json['medical_details'][member.pk][q.pk] = ''
                            for rq in q.related_questions.all():
                                 answer_json['medical_details'][member.pk][q.pk] = {'rq':{rq.pk:''}}
                                 
                        
                        answer_json['application_details'][member.pk] = {}
                        for q in application_questions:
                            answer_json['application_details'][member.pk][q.pk] = ''
                            for rq in q.related_questions.all():
                                 answer_json['application_details'][member.pk][q.pk] = {'rq':{rq.pk:''}}
                                 



                         
                    
                    questions = ''
                    j = {}
                    if provider:
                        questions = Question.objects.filter(insurers = provider)
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


            result = {
                'answer_json': answer_json,
                'question_json': arr,
            }
            return JsonResponse(result, safe=False)

        elif request.method == 'POST':
            print(request)
            j = json.loads(request.POST.get('data'))
            j['saved'] = True
            
            if maf.exists():
                maf = maf[0]
                saved_data = maf.qna_json
                if j['current_member'] == False:
                     if not j.get('next_question'):
                        j['current_stage'] = get_next_stage_integer(saved_data['current_stage'])
                for key, value in j.items():                    
                    if key == 'current_member' or key == 'current_stage':
                         saved_data[key] = j[key]
                    
                    if not isinstance(value, dict):
                        continue
                    for k,v in j[key].items():
                        saved_data[key][k] = j[key][k]
                    pass

                
                saved_data['current_member'] = j['current_member']
                
                maf.qna_json = j
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


def DocumentPDF(request, id):
    d = Deal.objects.filter(pk = id)
    deal = d[0] if d.exists() else None 
    quote = Quote.objects.filter(deal = deal) if deal else None
    quote = quote[0] if quote.exists() else None
        # deal = quote.deal if quote else None
    arr = {}
    answer_json = {}
    maf = MAF.objects.filter(quote = quote) if quote else None
    if maf and quote:
        order = Order.objects.filter(deal = deal) if deal else None
        provider = order[0].selected_plan.plan.insurer if order.exists() else None
        pdf_document = fitz.open('{}_maf.pdf'.format(provider.name.lower()))
        j = maf[0].qna_json
        applicant_details = j['applicants_details']
        medical_details = j['medical_details']
        application_details = j['application_details']
        p = 0
        w = 0
        for page in pdf_document:
            print(page)
            for w in page.widgets():
                print('{} -- {} -- {} -- {} -- {} -- {}'.format(w.field_name, w.field_label, w.field_type_string, w.field_value, w.choice_values ,w.button_states()))
                w.field_value = applicant_details.get(w.field_name.split(':')[0])
                w.update()
            
        pdf_document.save('filled')
        output_buffer = BytesIO()
        pdf_document.save(output_buffer)
        pdf_bytes = output_buffer.getvalue()
        pdf_document.close()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="' + 'abc.pdf' + '"'
        return response
        # return FileResponse(pdf_document, as_attachment=True, filename='abc.pdf')
     
    else:
          return "Quote doesn't exists"