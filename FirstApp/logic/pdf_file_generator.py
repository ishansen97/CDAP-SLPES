import jinja2 as ji
import pdfkit
import os
# from DemoProject import jinja2
from integrated_slpes import jinja2

def generate_pdf_file(object):

    # templateLoader = jinja2.FileSystemLoader(searchpath="../")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    TEMPLATE_DIR = os.path.join(BASE_DIR, "FirstApp\\templates\\FirstApp")
    HTML_PATH = os.path.join(TEMPLATE_DIR, "pdf_template_1.html")
    PDF_DIRECTORY = os.path.join(BASE_DIR, "FirstApp\\files")
    templateLoader = ji.FileSystemLoader(TEMPLATE_DIR)
    new_env = jinja2.environment()
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "pdf_template.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    print('variables: ', templateEnv.globals['dict'])


    # render the template
    outputText = template.render(lecturer_name=object['lecturer_name'], subject=object['subject_name'], date=object['date'], static=new_env.globals['static'])
    html_file = open(HTML_PATH, "w")
    html_file.write(outputText)
    html_file.close()

    # create a new pdf file path
    NEW_PDF_PATH = os.path.join(PDF_DIRECTORY, "activity.pdf")

    asset_path = os.path.join('D:/SLIIT/Year 4/CDAP/project/2020-101/assets/FirstApp/css/sb-admin-2.min.css')
    network_path = "file:/" + asset_path

    # options = {'enable-local-file-access': network_path}
    options = {'enable-local-file-access': asset_path, 'load-error-handling': 'ignore'}

    # create a new pdf file
    pdfkit.from_file(HTML_PATH, NEW_PDF_PATH, options=options)

