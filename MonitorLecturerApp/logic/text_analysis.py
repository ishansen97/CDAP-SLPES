import scripts
import re
import os

def run():

    # this dictionary will be returned
    analysis = {}

    # define the BASE path
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    FILE_PATH = os.path.join(BASE_PATH, "MonitorLecturerApp\\lecture_Notes\\sample_text2.txt")

    # regex = re.compile('[@!#$%^&*()<>?{}.,:;~_-]')
    #
    # if(regex.search(string) == None):
    #      print("String is accepted")
    # else:
    #      print("\nString is not accepted.\n")





    text = open(FILE_PATH, "r", encoding="utf8")

    d = dict()
    number_of_words = 0
    lexical_count = 0
    non_lexical_count = 0

    for line in text:
        line = line.strip()
        line = line.lower()

        line_text = line.split(" ")

        # incrementing the no. of words
        number_of_words += len(line_text)

        words = line.split(" ")

        for word in words:
            if word in d:
                d[word] = d[word] + 1
            else:
                d[word] = 1

    # the key words are "extraneous filler words(ok, well, like, Actually, Basically, that, jest, only, really, very, now, simply, maybe, perhaps, somehow, almost, slightly, seemed ....)"

    for key in list(d.keys()):
        if (key == "like"):
            lexical_count += d[key]
            # print('\n number of occurrences: (like)', d[key])

        elif (key == "ok"):
            lexical_count += d[key]
            # print('\n number of occurrences (ok)', d[key])

        elif(key == "now"):
            lexical_count += d[key]
            # print('\n number of occurrences (now)', d[key])

        elif (key == "simply"):
            lexical_count += d[key]
            # print('\n number of occurrences (simply)', d[key])

        elif (key == "well"):
            lexical_count += d[key]
            # print('\n number of occurrences (well)', d[key])

        elif (key == "actually"):
            lexical_count += d[key]
            # print('\n number of occurrences (actually)', d[key])

        elif (key == "basically"):
            lexical_count += d[key]
            # print('\n number of occurrences (basically)', d[key])

        elif (key == "that"):
            lexical_count += d[key]
            # print('\n number of occurrences (that)', d[key])

        # "jest" newei bn "just"
        elif (key == "just"):
            lexical_count += d[key]
            # print('\n number of occurrences (just)', d[key])

        elif (key == "only"):
            lexical_count += d[key]
            # print('\n number of occurrences (only)', d[key])

        elif (key == "really"):
            lexical_count += d[key]
            # print('\n number of occurrences (really)', d[key])

        elif (key == "very"):
            lexical_count += d[key]
            # print('\n number of occurrences (very)', d[key])

        elif (key == "maybe"):
            lexical_count += d[key]
            # print('\n number of occurrences (maybe)', d[key])

        elif (key == "perhaps"):
            lexical_count += d[key]
            # print('\n number of occurrences (perhaps)', d[key])

        elif (key == "somehow"):
            lexical_count += d[key]
            # print('\n number of occurrences (somehow)', d[key])

        elif (key == "almost"):
            lexical_count += d[key]
            # print('\n number of occurrences (almost)', d[key])

        elif (key == "slightly"):
            lexical_count += d[key]
            # print('\n number of occurrences (slightly)', d[key])

        elif (key == "seemed"):
            lexical_count += d[key]
            # print('\n number of occurrences (seemed)', d[key])


    # "non-lexical filled pauses(um, uh, erm, hmm, uuh, er,  ....)"


        elif(key == "hmm"):
           non_lexical_count += d[key]
           # print('\n number of occurrences (hmm)', d[key])

        elif (key == "um"):
            non_lexical_count += d[key]
            # print('\n number of occurrences (um)', d[key])

        elif (key == "uh"):
            non_lexical_count += d[key]
            # print('\n number of occurrences (uh)', d[key])

        elif (key == "erm"):
            non_lexical_count += d[key]
            # print('\n number of occurrences (erm)', d[key])

        elif (key == "er"):
            non_lexical_count += d[key]
            # print('\n number of occurrences (er)', d[key])

        elif (key == "uuh"):
            non_lexical_count += d[key]
            # print('\n number of occurrences (uuh)', d[key])



    data = text.read()
    num_words = data.split("\n")

    # print("\nThe number of words in the document : ", number_of_words)
    #
    #
    # print("\nNumber of extraneous filler words spoken : ", lexical_count)
    #
    #
    # print("\nNumber of non-lexical filled pauses spoken : ", non_lexical_count )


    # returning the values
    analysis['num_of_words'] = number_of_words
    analysis['lexical_count'] = lexical_count
    analysis['non_lexical_count'] = non_lexical_count

    return analysis
