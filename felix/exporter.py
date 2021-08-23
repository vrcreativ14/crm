import csv
import logging
import datetime
from django.http import HttpResponse


api_logger = logging.getLogger("api.exporter")


class ExportService:
    def to_csv(self, column_labels=[], data=[], filename='export.csv'):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(column_labels)
        for d in data:
            writer.writerow(d)

        return response
