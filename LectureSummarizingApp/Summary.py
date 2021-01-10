from spacy.lang.pt.stop_words import STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
import pt_core_news_sm
import os
from fpdf import FPDF

def LectureSummary(summary_name):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH = os.path.join(BASE_DIR, "speechToText\\{}".format(summary_name))
    print('file path: ' , FILE_PATH)
    DESTINATION_DIR = os.path.join(BASE_DIR, "summary\\Summary_{}".format(summary_name))
    print('destination directory: ', DESTINATION_DIR)

    print('starting the summary process')


# Reading the file
    nlp = pt_core_news_sm.load()
    # file = open(DESTINATION_DIR, 'w')
    text = ''
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        text = " ".join(f.readlines())

    doc = nlp(text)

#calculating the word frequency
    corpus = [sent.text.lower() for sent in doc.sents ]
    cv = CountVectorizer(stop_words=list(STOP_WORDS))
    cv_fit=cv.fit_transform(corpus)
    word_list = cv.get_feature_names()
    count_list = cv_fit.toarray().sum(axis=0)
    word_frequency = dict(zip(word_list,count_list))


    val=sorted(word_frequency.values())
    higher_word_frequencies = [word for word,freq in word_frequency.items() if freq in val[-3:]]
    print("\nWords with higher frequencies: ", higher_word_frequencies)
    # gets relative frequency of words
    higher_frequency = val[-1]
    for word in word_frequency.keys():
        word_frequency[word] = (word_frequency[word]/higher_frequency)

#calculating sentence rank and taking top ranked sentences for the summary
    sentence_rank={}
    for sent in doc.sents:
        for word in sent :
            if word.text.lower() in word_frequency.keys():
                if sent in sentence_rank.keys():
                    sentence_rank[sent]+=word_frequency[word.text.lower()]
                else:
                    sentence_rank[sent]=word_frequency[word.text.lower()]
    top_sentences=(sorted(sentence_rank.values())[::-1])
    top_sent=top_sentences[:3]

    summary=[]
    for sent,strength in sentence_rank.items():
        if strength in top_sent:
            summary.append(sent)
        else:
            continue


    file = None
    for i in summary:
        file = open(DESTINATION_DIR, 'w')
        # file = open('Summary01.txt', 'w')
        file.write(str(i))
        file.close()



# def SaveSummary():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # PDF_DESTINATION_DIR = os.path.dirname(os.path.join(BASE_DIR, "summaryPDF\\sample.txt"))
    PDF_DESTINATION_DIR = os.path.join(BASE_DIR, "summaryPDF\\Summary_PDF_{}.pdf".format(summary_name))

    pdf = FPDF()
    # Add a page
    pdf.add_page()
    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size=15)

    # open the text file in read mode
    f = open(DESTINATION_DIR, "r")

    # insert the texts in pdf
    for x in f:
        pdf.cell(200, 10, txt=x, ln=1, align='C')

    # save the pdf with name .pdf
    # pdf.output(PDF_DESTINATION_DIR)

    # convert the summary list to a text
    listToStr = ' '.join([str(elem) for elem in summary])

    print('ending the summary process')

    return text, listToStr