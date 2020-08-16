import re

def custom_sort(array):

    number_arr = []

    for words in array:
        result = [int(s) for s in re.findall(r'\b\d+\b', words)]
        new_number = result[0] if len(result) == 1 else 0
        number_arr.append(int(new_number))

    sorted_num_arr = sorted(number_arr)

    set_number = set(sorted_num_arr)

    list_set_number = list(set_number)

    new_arr = [0 for i in range(len(list_set_number))]

    for word in array:

        result = [int(s) for s in re.findall(r'\b\d+\b', word)]
        new_number = result[0] if len(result) == 1 else 0
        number = int(new_number)

        if number in list_set_number:
            index = list_set_number.index(number)
            new_arr[index] = word

    return new_arr


def custom_object_sorter(obj_array):
    # this list will keep the extracted keys
    key_arr = []
    # this list will returned the ordered object array
    new_obj_array = [0 for i in range(len(obj_array))]

    # this loop will extract the keys and append to the defined list
    for obj in obj_array:
        key_list = list(obj.keys())
        main_key = key_list[0]
        key_arr.append(obj[main_key])

    # this method will arrange the keys in the order
    sorted_keys = custom_sort(key_arr)

    # iterate through the object array once again, to arrange them in the correct order
    for obj in obj_array:
        key_list = list(obj.keys())
        main_key = key_list[0]

        # compare the main key element and the ordered key list
        if obj[main_key] in sorted_keys:
            index = sorted_keys.index(obj[main_key])
            # assign to the new list according to the given index
            new_obj_array[index] = obj

    return new_obj_array