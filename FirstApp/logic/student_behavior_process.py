import pandas as pd
from . import utilities as ut

def calculate_student_activity_emotion_correlations(lec_activities, lec_emotions):
    # this variable will be used to store the correlations
    correlations = []

    # limit = 10
    limit = len(lec_activities)

    data_index = ['lecture-{}'.format(i + 1) for i in range(len(lec_activities))]

    # define the correlation data dictionary
    corr_data = {}

    # student gaze labels
    student_activity_labels = ['phone checking', 'listening', 'note taking']
    student_emotion_labels = ['Happy', 'Sad', 'Angry', 'Surprise', 'Neutral']

    # lecture activity data list (student)
    phone_perct_list = []
    note_perct_list = []
    listen_perct_list = []

    # lecture emotion data list (student)
    happy_perct_list = []
    sad_perct_list = []
    angry_perct_list = []
    surprise_perct_list = []
    neutral_perct_list = []


    # loop through the lecture activity data
    for data in lec_activities:
        value = int(data['phone_perct'])
        value1 = int(data['listening_perct'])
        value2= int(data['writing_perct'])

        if value != 0:
            phone_perct_list.append(int(data['phone_perct']))
        if value1 != 0:
            listen_perct_list.append(int(data['listening_perct']))
        if value2 != 0:
            note_perct_list.append(int(data['writing_perct']))

    # loop through the lecture emotion data
    for data in lec_emotions:
        value = int(data['happy_perct'])
        value1 = int(data['sad_perct'])
        value2 = int(data['angry_perct'])
        value3 = int(data['surprise_perct'])
        value4 = int(data['neutral_perct'])

        if value != 0:
            happy_perct_list.append(int(data['happy_perct']))
        if value1 != 0:
            sad_perct_list.append(int(data['sad_perct']))
        if value2 != 0:
            angry_perct_list.append(int(data['angry_perct']))
        if value3 != 0:
            surprise_perct_list.append(int(data['surprise_perct']))
        if value4 != 0:
            neutral_perct_list.append(int(data['neutral_perct']))


    if len(phone_perct_list) == len(lec_activities):
        corr_data[student_activity_labels[0]] = phone_perct_list
    if len(listen_perct_list) == len(lec_activities):
        corr_data[student_activity_labels[1]] = listen_perct_list
    if len(note_perct_list) == len(lec_activities):
        corr_data[student_activity_labels[2]] = note_perct_list
    if len(happy_perct_list) == len(lec_activities):
        corr_data[student_emotion_labels[0]] = happy_perct_list
    if len(sad_perct_list) == len(lec_activities):
        corr_data[student_emotion_labels[1]] = sad_perct_list
    if len(angry_perct_list) == len(lec_activities):
        corr_data[student_emotion_labels[2]] = angry_perct_list
    if len(surprise_perct_list) == len(lec_activities):
        corr_data[student_emotion_labels[3]] = surprise_perct_list
    if len(neutral_perct_list) == len(lec_activities):
        corr_data[student_emotion_labels[4]] = neutral_perct_list

    # corr_data = {'phone checking': phone_perct_list, 'listening': listen_perct_list, 'note taking': note_perct_list,
    #              'Happy': happy_perct_list, 'Sad': sad_perct_list, 'Angry': angry_perct_list, 'Surprise': surprise_perct_list, 'Neutral': neutral_perct_list,
    #              }

    print('data: ', corr_data)

    # create the dataframe
    df = pd.DataFrame(corr_data, index=data_index)
    df = df[(df.T != 0).any()]

    print(df)

    # calculate the correlation
    pd_series = ut.get_top_abs_correlations(df, limit)

    print(pd_series)

    # assign a new value to the 'limit' variable
    limit = len(pd_series) if len(pd_series) < limit else limit

    for i in range(limit):
        # this dictionary will get the pandas.Series object's  indices and values separately
        corr_dict = {}

        index = pd_series.index[i]

        # check whether the first index is a student activity
        isStudentActivity = index[0] in student_activity_labels
        # check whether the second index is a lecturer activity
        isStudentEmotion = index[1] in student_emotion_labels

        # if both are student and lecturer activities, add to the dictionary
        if isStudentActivity & isStudentEmotion:
            corr_dict['index'] = index
            corr_dict['value'] = pd_series.values[i]

            # append the dictionary to the 'correlations' list
            correlations.append(corr_dict)


    # return the list
    return correlations


# this method will calculate the student activity-gaze correlations
def calculate_student_activity_gaze_correlations(lec_activities, lec_gaze):
    # this variable will be used to store the correlations
    correlations = []

    limit = len(lec_activities)

    data_index = ['lecture-{}'.format(i + 1) for i in range(len(lec_activities))]

    # this dictionary contains the correlation data
    corr_data = {}

    # student gaze labels
    student_activity_labels = ['phone checking', 'listening', 'note taking']
    # student_emotion_labels = ['Happy', 'Sad', 'Angry', 'Surprise', 'Neutral']
    student_gaze_labels = ['Up and Right', 'Up and Left', 'Down and Right', 'Down and Left', 'Front']

    # lecture activity data list (student)
    phone_perct_list = []
    note_perct_list = []
    listen_perct_list = []

    # lecture gaze estimation data list (student)
    upright_perct_list = []
    upleft_perct_list = []
    downright_perct_list = []
    downleft_perct_list = []
    front_perct_list = []


    # loop through the lecture activity data
    for data in lec_activities:
        value = int(data['phone_perct'])
        value1 = int(data['listening_perct'])
        value2 = int(data['writing_perct'])

        if value != 0:
            phone_perct_list.append(int(data['phone_perct']))
        if value1 != 0:
            listen_perct_list.append(int(data['listening_perct']))
        if value2 != 0:
            note_perct_list.append(int(data['writing_perct']))

    # loop through the lecture activity data
    for data in lec_gaze:
        value = int(data['looking_up_and_right_perct'])
        value1 = int(data['looking_up_and_left_perct'])
        value2 = int(data['looking_down_and_right_perct'])
        value3 = int(data['looking_down_and_left_perct'])
        value4 = int(data['looking_front_perct'])

        if value != 0:
            upright_perct_list.append(int(data['looking_up_and_right_perct']))
        if value1 != 0:
            upleft_perct_list.append(int(data['looking_up_and_left_perct']))
        if value2 != 0:
            downright_perct_list.append(int(data['looking_down_and_right_perct']))
        if value3 != 0:
            downleft_perct_list.append(int(data['looking_down_and_left_perct']))
        if value4 != 0:
            front_perct_list.append(int(data['looking_front_perct']))


    if (len(phone_perct_list)) == len(lec_activities):
        corr_data[student_activity_labels[0]] = phone_perct_list
    if (len(listen_perct_list)) == len(lec_activities):
        corr_data[student_activity_labels[1]] = listen_perct_list
    if (len(note_perct_list)) == len(lec_activities):
        corr_data[student_activity_labels[2]] = note_perct_list
    if (len(upright_perct_list)) == len(lec_activities):
        corr_data[student_gaze_labels[0]] = upright_perct_list
    if (len(upleft_perct_list)) == len(lec_activities):
        corr_data[student_gaze_labels[1]] = upleft_perct_list
    if (len(downright_perct_list)) == len(lec_activities):
        corr_data[student_gaze_labels[2]] = downright_perct_list
    if (len(downleft_perct_list)) == len(lec_activities):
        corr_data[student_gaze_labels[3]] = downleft_perct_list
    if (len(front_perct_list)) == len(lec_activities):
        corr_data[student_gaze_labels[4]] = front_perct_list

    # corr_data = {'phone checking': phone_perct_list, 'listening': listen_perct_list, 'note taking': note_perct_list,
    #              'Up and Right': upright_perct_list, 'Up and Left': upleft_perct_list, 'Down and Right': downright_perct_list,
    #              'Down and Left': downleft_perct_list, 'Front': front_perct_list
    #              }

    # create the dataframe
    df = pd.DataFrame(corr_data, index=data_index)

    print(df)

    # calculate the correlation
    pd_series = ut.get_top_abs_correlations(df, limit)

    print(pd_series)
    print('length of pd_series: ', len(pd_series))

    # assign a new value to the 'limit' variable
    limit = len(pd_series) if len(pd_series) < limit else limit

    for i in range(limit):
        # this dictionary will get the pandas.Series object's  indices and values separately
        corr_dict = {}

        index = pd_series.index[i]

        # check whether the first index is a student activity
        isStudentActivity = index[0] in student_activity_labels
        # check whether the second index is a student gaze estimation
        isStudentGaze = index[1] in student_gaze_labels

        # if both are student and lecturer activities, add to the dictionary
        if isStudentActivity & isStudentGaze:
            corr_dict['index'] = index
            corr_dict['value'] = pd_series.values[i]

            # append the dictionary to the 'correlations' list
            correlations.append(corr_dict)

            print('correlations: ', correlations)

    # return the list
    return correlations


# this method will calculate the student activity-gaze correlations
def calculate_student_emotion_gaze_correlations(lec_emotions, lec_gaze):
    # this variable will be used to store the correlations
    correlations = []

    limit = len(lec_emotions)

    data_index = ['lecture-{}'.format(i + 1) for i in range(len(lec_emotions))]

    # this dictionary will contain the correlation data
    corr_data = {}

    student_emotion_labels = ['Happy', 'Sad', 'Angry', 'Surprise', 'Neutral']
    student_gaze_labels = ['Up and Right', 'Up and Left', 'Down and Right', 'Down and Left', 'Front']


    # lecture emotion data list (student)
    happy_perct_list = []
    sad_perct_list = []
    angry_perct_list = []
    surprise_perct_list = []
    neutral_perct_list = []

    # lecture gaze estimation data list (student)
    upright_perct_list = []
    upleft_perct_list = []
    downright_perct_list = []
    downleft_perct_list = []
    front_perct_list = []


    # loop through the lecture emotion data
    for data in lec_emotions:
        value = int(data['happy_perct'])
        value1 = int(data['sad_perct'])
        value2 = int(data['angry_perct'])
        value3 = int(data['surprise_perct'])
        value4 = int(data['neutral_perct'])

        if value != 0:
            happy_perct_list.append(int(data['happy_perct']))
        if value1 != 0:
            sad_perct_list.append(int(data['sad_perct']))
        if value2 != 0:
            angry_perct_list.append(int(data['angry_perct']))
        if value3 != 0:
            surprise_perct_list.append(int(data['surprise_perct']))
        if value4 != 0:
            neutral_perct_list.append(int(data['neutral_perct']))

    # loop through the lecture gaze data
    for data in lec_gaze:
        value = int(data['looking_up_and_right_perct'])
        value1 = int(data['looking_up_and_left_perct'])
        value2 = int(data['looking_down_and_right_perct'])
        value3 = int(data['looking_down_and_left_perct'])
        value4 = int(data['looking_front_perct'])

        if value != 0:
            upright_perct_list.append(int(data['looking_up_and_right_perct']))
        if value1 != 0:
            upleft_perct_list.append(int(data['looking_up_and_left_perct']))
        if value2 != 0:
            downright_perct_list.append(int(data['looking_down_and_right_perct']))
        if value3 != 0:
            downleft_perct_list.append(int(data['looking_down_and_left_perct']))
        if value4 != 0:
            front_perct_list.append(int(data['looking_front_perct']))


    if len(happy_perct_list) == len(lec_emotions):
        corr_data[student_emotion_labels[0]] = happy_perct_list
    if len(sad_perct_list) == len(lec_emotions):
        corr_data[student_emotion_labels[1]] = sad_perct_list
    if len(angry_perct_list) == len(lec_emotions):
        corr_data[student_emotion_labels[2]] = angry_perct_list
    if len(surprise_perct_list) == len(lec_emotions):
        corr_data[student_emotion_labels[3]] = surprise_perct_list
    if len(neutral_perct_list) == len(lec_emotions):
        corr_data[student_emotion_labels[4]] = neutral_perct_list
    if (len(upright_perct_list)) == len(lec_emotions):
        corr_data[student_gaze_labels[0]] = upright_perct_list
    if (len(upleft_perct_list)) == len(lec_emotions):
        corr_data[student_gaze_labels[1]] = upleft_perct_list
    if (len(downright_perct_list)) == len(lec_emotions):
        corr_data[student_gaze_labels[2]] = downright_perct_list
    if (len(downleft_perct_list)) == len(lec_emotions):
        corr_data[student_gaze_labels[3]] = downleft_perct_list
    if (len(front_perct_list)) == len(lec_emotions):
        corr_data[student_gaze_labels[4]] = front_perct_list



    # corr_data = {'Happy': happy_perct_list, 'Sad': sad_perct_list, 'Angry': angry_perct_list, 'Surprise': surprise_perct_list, 'Neutral': neutral_perct_list,
    #              'Up and Right': upright_perct_list, 'Up and Left': upleft_perct_list, 'Down and Right': downright_perct_list,
    #              'Down and Left': downleft_perct_list, 'Front': front_perct_list
    #              }

    # create the dataframe
    df = pd.DataFrame(corr_data, index=data_index)

    print(df)

    # calculate the correlation
    pd_series = ut.get_top_abs_correlations(df, limit)

    print(pd_series)

    # assign a new value to the 'limit' variable
    limit = len(pd_series) if len(pd_series) < limit else limit

    for i in range(limit):
        # this dictionary will get the pandas.Series object's  indices and values separately
        corr_dict = {}

        index = pd_series.index[i]

        # check whether the first index is a student activity
        isStudentEmotion = index[0] in student_emotion_labels
        # check whether the second index is a student gaze estimation
        isStudentGaze = index[1] in student_gaze_labels

        # if both are student and lecturer activities, add to the dictionary
        if isStudentEmotion & isStudentGaze:
            corr_dict['index'] = index
            corr_dict['value'] = pd_series.values[i]

            # append the dictionary to the 'correlations' list
            correlations.append(corr_dict)

    # return the list
    return correlations


# this method will provide comments on the student behavior
def generate_student_behavior_comments(category, **kwargs):

    # declare the comments list
    comments = []

    if category == "Activity":
        float_phone_perct = float(kwargs.get('phone_perct'))
        float_listen_perct = float(kwargs.get('listen_perct'))
        float_note_perct = float(kwargs.get('note_perct'))

        # set the threshold value list
        THRESHOLDS = [40, 20, 30]


        if int(float_phone_perct) >= THRESHOLDS[0]:
            comments.append("Special Attention needs to be given to reduce student phone checking")
        if int(float_listen_perct) < THRESHOLDS[1]:
            comments.append("Consider taking steps to increase student attention")
        if int(float_note_perct) < THRESHOLDS[2]:
            comments.append("Try to pursue students to take important notes during the lecture")


    elif category == "Emotion":
        print('Emotion')
    elif category == "Gaze":
        print('Gaze')


    # return the comment list
    return comments
