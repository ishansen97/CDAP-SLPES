def generate_new_id(prev_id):

    alpha = []
    digit_index = 0
    value_index = 0
    zero_index = 0
    count = 0
    text_len = len(prev_id)

    for letter in list(prev_id):

        if (letter.isalpha()):
            alpha.append(letter)

        if (letter.isdigit()):
            digit_index = count
            break

        count += 1

    print('digit index: ', digit_index)

    zero_index = digit_index

    for i in range(digit_index, text_len):
        if (prev_id[i] == '0'):
            zero_index += 1
        else:
            value_index = i
            break

    sub_text = prev_id[value_index:text_len]
    number = int(sub_text)
    number += 1

    number_str = str(number)
    len_number_str = len(number_str)
    num_of_zeros = text_len - (len_number_str + digit_index)
    zero_text = ''
    new_str = ''
    returned_id = prev_id

    # converting the list into a string
    for l in alpha:
        new_str += l

    if (num_of_zeros >= 0):

        for i in range(0, num_of_zeros):
            zero_text += '0'

        returned_id = new_str + zero_text + number_str

    # returning the new id
    if (returned_id == prev_id):
        return prev_id

    return returned_id