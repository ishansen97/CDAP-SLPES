import nltk
import os
from fpdf import FPDF

def GetLectureNotice(notice_name):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH = os.path.join(BASE_DIR, "speechToText\\{}".format(notice_name))
    DESTINATION_DIR = os.path.join(BASE_DIR, "notices\\Notice_{}".format(notice_name))
    print('destination directory: ', DESTINATION_DIR)

    text = ''
    read_lines = [line.rstrip('\n') for line in open(FILE_PATH, "r")]
    sentences_list = []
    sentence_list = nltk.sent_tokenize(read_lines)
    word_search = "important"
    sentences_with_word = []
    for sentence in sentence_list:
        if sentence.count(word_search)>0:
            sentences_with_word.append(sentence)

    words_search = ["exam", "assignment"]
    word_sentence_dictionary = {"exam":[],"assignment":[]}

    for word in words_search:
        sentences_with_word = []
        for sentence in sentences_list:
            if sentence.count(word)>0:
                sentences_with_word.append(sentence)
                word_sentence_dictionary[word] = sentences_with_word

    file = open('DESTINATION_DIR', 'w')
    file.close()


# def SaveNotices():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # PDF_DESTINATION_DIR = os.path.dirname(os.path.join(BASE_DIR, "summaryPDF\\sample.txt"))
    PDF_DESTINATION_DIR = os.path.join(BASE_DIR, "noticePDF\\Notice{}.pdf".format(notice_name))


    pdf = FPDF()
    # Add a page
    pdf.add_page()
    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size=15)

    # open the text file in read mode
    f = open("DESTINATION_DIR", "r")

    # insert the texts in pdf
    for x in f:
        pdf.cell(200, 10, txt=x, ln=1, align='C')

    # save the pdf with name .pdf
    pdf.output("PDF_DESTINATION_DIR")

    listToStr = ' '.join([str(elem) for elem in sentences_with_word])

    return text, listToStr