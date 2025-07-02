import io
import logging

from django.contrib.auth.models import User

from core.email import Emailer
from core.models import Note
from core.pdf import PDF
from customers.models import Customer
from felix.celery_app import app
from felix.sms import SMSService
from motorinsurance.models import Deal, CustomerProfile
from motorinsurance.models import Lead, Quote
from motorinsurance_shared.models import Product


@app.task
def create_deal_from_lead(lead: Lead, form_data=None):
    logger = logging.getLogger('workers')
    logger.info('Creating a customer and deal for motor insurance lead. Lead id: {}'.format(lead.pk))

    customer = Customer.objects.create(
        company=lead.company,
        name=lead.name,
        email=lead.email,
        phone=lead.contact_number,
        dob=lead.dob,
        nationality=lead.nationality
    )
    logger.info('Customer id {}'.format(customer.pk))

    customer_profile = CustomerProfile.objects.create(
        customer=customer,
        first_license_country=lead.first_license_country,
        first_license_age=lead.first_license_age,
        uae_license_age=lead.uae_license_age
    )
    logger.info('Customer profile id {}'.format(customer_profile.pk))

    deal = Deal.objects.create(
        customer=customer,

        company=lead.company,
        lead=lead,
        lead_type=lead.lead_type,
        car_year=lead.car_year,
        car_make=lead.car_make,
        car_trim=lead.car_trim,
        custom_car_name=lead.custom_car_name,
        current_insurer=lead.current_insurer,
        current_insurance_type=lead.current_insurance_type,
        date_of_first_registration=lead.date_of_first_registration,
        place_of_registration=lead.place_of_registration,
        vehicle_insured_value=lead.vehicle_insured_value,
        years_without_claim=lead.years_without_claim,
        claim_certificate_available=lead.claim_certificate_available,
        private_car=lead.private_car,
        car_unmodified=lead.car_unmodified,
        car_gcc_spec=lead.car_gcc_spec
    )

    user_id = form_data.get('user_id')

    if user_id:
        try:
            user = User.objects.get(pk=user_id)

            if user.userprofile.has_producer_role():
                deal.producer = user
            else:
                deal.assigned_to = user

            deal.save()
        except User.DoesNotExist:
            logger.error('Motor lead form submitted with user id which doesn\'t exists {}'.format(user_id))
            pass

    logger.info('Motor insurance deal id {}'.format(deal.pk))

    logger.info('Sending lead received email for lead id {}'.format(lead.pk))
    emailer = Emailer(lead.company)
    emailer.send_lead_received_email(deal)

    sms = SMSService()
    if deal.customer.phone:
        message = f'Thank you for requesting car insurance quotes from {lead.company.name}. We\'re preparing some options for you and will send you an email soon!'
        sms.send_sms(deal.customer.phone, message)

    return deal


@app.task
def perform_successful_product_selection(quote: Quote, product, qp_id, add_ons=False,
                                         policy_start_date='', bank_finance='', send_email=False, send_sms=False):
    quote.selected_product_details = {
        'product_id': product.id,
        'quoted_product_id': qp_id,
        'product_name': product.name,
        'add_ons': add_ons,
        'policy_start_date': policy_start_date,
        'bank_finance': bank_finance
    }
    quote.save()

    deal = quote.deal
    order = deal.get_order()
    attachments = None

    if send_email:
        if order:
            source = order.get_pdf_url()
            pdf = PDF().get_pdf_content(source)
            file = io.BytesIO(pdf)
            attachments = [('order-summary.pdf', file)]

        emailer = Emailer(quote.company)
        emailer.send_order_confirmation_email(deal, attachments)

        if deal.assigned_to and deal.assigned_to.userprofile.email_when_new_order_placed:
            emailer.send_order_confirmation_email_to_agent(deal)

    if send_sms:
        sms = SMSService()

        if deal.customer.phone:
            document_upload_url = quote.get_document_upload_short_url()
            message = f'Hi {deal.customer.name}, thanks for your order! Please upload your documents here so we can issue your policy: {document_upload_url}'
            sms.send_sms(deal.customer.phone, message)


@app.task
def add_note_to_deal(attached_to, content):
    # Adding note to the deal with user selected product details
    note = Note(
        attached_to=attached_to,
        note_type=Note.NOTE_TEXT,
        note_direction=Note.DIRECTION_IN,
        system_generated=True,
        content=content
    )

    note.save()


@app.task
def removed_selected_product_and_add_a_note(quote: Quote, user):
    formatted_add_ons = ''

    if quote.selected_product_details:
        product_id = quote.selected_product_details['product_id']
        product = Product.objects.get(pk=product_id)

        if 'add_ons' in quote.selected_product_details:
            for add_on in quote.selected_product_details['add_ons']:
                formatted_add_ons += f'<span class="badge badge-primary">{add_on}</span> '

        # Adding note to the deal with user selected product details
        note = Note(
            attached_to=quote.deal,
            note_type=Note.NOTE_TEXT,
            note_direction=Note.DIRECTION_NONE,
            system_generated=True,
            content='Product <span class="badge badge-primary">{}</span> with Addon {} selection cleared by {}'.format(
                product,
                formatted_add_ons,
                user
            )
        )

        note.save()

        quote.selected_product_details = None
        quote.save()

        quote.deal.status = Deal.STATUS_QUOTE_SENT
        quote.deal.save()
