"""PDF Generation"""
import time
import logging
import requests
import docraptor

from django.conf import settings
from django.http import HttpResponse


class PDF:
    def __init__(self):
        self.doc_api = docraptor.DocApi()
        self.doc_api.api_client.configuration.username = settings.DOCRAPTOR_API_KEY
        self.logger = logging.getLogger('api.docraptor')

    def convert(self, source='', filename='file.pdf', is_url=True):
        pdf_content = self.get_pdf_content(source, filename, is_url)

        response = HttpResponse(pdf_content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    def get_pdf_content(self, source, filename='file.pdf', is_url=True):
        options = {
            "test": settings.DEBUG,
            "name": filename,
            "document_type": "pdf",
            "javascript": True,
            "prince_options": {
                "media": "screen"
            }
        }

        if is_url:
            options['document_url'] = source
        else:
            options['document_content'] = source

        try:
            pdf_content = ''
            timeout = time.time() + 60 * 2  # 2 minutes
            response = self.doc_api.create_async_doc(options)

            while True:
                if time.time() > timeout:
                    self.logger.error('PDF generation timed out, source: {}'.format(source))
                    break

                status_response = self.doc_api.get_async_doc_status(response.status_id)

                if status_response.status == "completed":
                    pdf_content = self.doc_api.get_async_doc(status_response.download_id)
                    break
                elif status_response.status == "failed":
                    self.logger.error('PDF generation failed response: {}'.format(status_response))
                    break
                else:
                    time.sleep(1)

        except docraptor.rest.ApiException as error:
            self.logger.error('PDF generation exception raised. Error: {}'.format(error))

        return pdf_content
