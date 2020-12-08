import pandas as pd
from . import utilities as ut

def calculate_student_activity_emotion_correlations(lec_activities, lec_emotions):
    # this variable will be used to store the correlations
    correlations = []

    limit = 10

    data_index = ['lecture-{}'.format(i + 1) for i in range(len(lec_activities))]

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
        phone_perct_list.append(int(data['phone_perct']))
        listen_perct_list.append(int(data['listening_perct']))
        note_perct_list.append(int(data['writing_perct']))

    # loop through the lecture emotion data
    for data in lec_emotions:
        happy_perct_list.append(int(data['happy_perct']))
        sad_perct_list.append(int(data['sad_perct']))
        angry_perct_list.append(int(data['angry_perct']))
        surprise_perct_list.append(int(data['surprise_perct']))
        neutral_perct_list.append(int(data['neutral_perct']))


    corr_data = {'phone checking': phone_perct_list, 'listening': listen_perct_list, 'note taking': note_perct_list,
                 'Happy': happy_perct_list, 'Sad': sad_perct_list, 'Angry': angry_perct_list, 'Surprise': surprise_perct_list, 'Neutral': neutral_perct_list,
                 }

    # create the dataframe
    df = pd.DataFrame(corr_data, index=data_index)

    # calculate the correlation
    pd_series = ut.get_top_abs_correlations(df, limit)

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

    limit = 10

    data_index = ['lecture-{}'.format(i + 1) for i in range(len(lec_activities))]

    # student gaze labels
    student_activity_labels = ['phone checking', 'listening', 'note taking']
    student_emotion_labels = ['Happy', 'Sad', 'Angry', 'Surprise', 'Neutral']
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
        phone_perct_list.append(int(data['phone_perct']))
        listen_perct_list.append(int(data['listening_perct']))
        note_perct_list.append(int(data['writing_perct']))

    # loop through the lecture activity data
    for data in lec_gaze:
        upright_perct_list.append(int(data['looking_up_and_right_perct']))
        upleft_perct_list.append(int(data['looking_up_and_left_perct']))
        downright_perct_list.append(int(data['looking_down_and_right_perct']))
        downleft_perct_list.append(int(data['looking_down_and_left_perct']))
        front_perct_list.append(int(data['looking_front_perct']))


    corr_data = {'phone checking': phone_perct_list, 'listening': listen_perct_list, 'note taking': note_perct_list,
                 'Up and Right': upright_perct_list, 'Up and Left': upleft_perct_list, 'Down and Right': downright_perct_list,
                 'Down and Left': downleft_perct_list, 'Front': front_perct_list
                 }

    # create the dataframe
    df = pd.DataFrame(corr_data, index=data_index)

    # calculate the correlation
    pd_series = ut.get_top_abs_correlations(df, limit)

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

    # return the list
    return correlations


# this method will calculate the student activity-gaze correlations
def calculate_student_emotion_gaze_correlations(lec_emotions, lec_gaze):
    # this variable will be used to store the correlations
    correlations = []

    limit = 10

    data_index = ['lecture-{}'.format(i + 1) for i in range(len(lec_emotions))]

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
        happy_perct_list.append(int(data['happy_perct']))
        sad_perct_list.append(int(data['sad_perct']))
        angry_perct_list.append(int(data['angry_perct']))
        surprise_perct_list.append(int(data['surprise_perct']))
        neutral_perct_list.append(int(data['neutral_perct']))

    # loop through the lecture gaze data
    for data in lec_gaze:
        upright_perct_list.append(int(data['looking_up_and_right_perct']))
        upleft_perct_list.append(int(data['looking_up_and_left_perct']))
        downright_perct_list.append(int(data['looking_down_and_right_perct']))
        downleft_perct_list.append(int(data['looking_down_and_left_perct']))
        front_perct_list.append(int(data['looking_front_perct']))


    corr_data = {'Happy': happy_perct_list, 'Sad': sad_perct_list, 'Angry': angry_perct_list, 'Surprise': surprise_perct_list, 'Neutral': neutral_perct_list,
                 'Up and Right': upright_perct_list, 'Up and Left': upleft_perct_list, 'Down and Right': downright_perct_list,
                 'Down and Left': downleft_perct_list, 'Front': front_perct_list
                 }

    # create the dataframe
    df = pd.DataFrame(corr_data, index=data_index)

    # calculate the correlation
    pd_series = ut.get_top_abs_correlations(df, limit)

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