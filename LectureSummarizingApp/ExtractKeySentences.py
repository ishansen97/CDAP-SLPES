import nltk
import os
from fpdf import FPDF

def LectureNotice(notice_name):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH = os.path.join(BASE_DIR, "speechToText\\{}".format(notice_name))
    DESTINATION_DIR = os.path.dirname(os.path.join(BASE_DIR, "LectureSummarizingApp\\Notices\\sample.txt"))
    print('destination directory: ', DESTINATION_DIR)

    read_lines = [line.rstrip('\n') for line in open("audioToText01.txt", "r")]
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


def SaveNotices():
    pdf = FPDF()
    # Add a page
    pdf.add_page()
    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size=15)

    # open the text file in read mode
    f = open("Summary01.txt", "r")

    # insert the texts in pdf
    for x in f:
        pdf.cell(200, 10, txt=x, ln=1, align='C')

    # save the pdf with name .pdf
    pdf.output("summary01.pdf")