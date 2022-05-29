from django.http import HttpResponse, HttpResponseServerError
from django.template.loader import get_template
from xhtml2pdf import pisa

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import os


def render_borrow_log_to_pdf(template_src, pdf_name, context_dict={}):
    template = get_template(template_src)
    borrow_count = context_dict['borrow_count']
    return_count = context_dict['return_count']

    if borrow_count == 0 and return_count == 0:
        return HttpResponseServerError('There is no report to generate')

    # Create the chart for the rendering
    plt.pie(
        [borrow_count, return_count],
        autopct='%1.1f%%',
        labels=[f'Borrowed: {borrow_count}', f'Returned: {return_count}'],
    )
    chart_save_path = os.path.join(os.path.dirname(__file__), 'static', 'image', 'chart.png')

    # Save the chart
    plt.savefig(chart_save_path, dpi=300)
    plt.close()

    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{pdf_name}"'

    pdf_status = pisa.CreatePDF(html, dest=response)

    if pdf_status.err:
        return HttpResponseServerError('Some errors were encountered <pre>' + html + '</pre>')

    return response