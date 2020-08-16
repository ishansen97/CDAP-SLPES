import cv2
import os
import re
import base64
import shutil


def saveImage(response):


    dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
    base_path = os.path.join(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(base_path))
    new_dir_name = "static\\FirstApp\\images\\{}".format(response["imageName"])
    new_dir = os.path.join(root_dir, new_dir_name)

    if (os.path.isdir(new_dir)):
        # delete the previous directory
        shutil.rmtree(new_dir)

    # create the new directory
    os.mkdir(new_dir)


    count = 0

    for url in response["ImageURLS"]:
        url = dataUrlPattern.match(url).group(2)
        encoded = url.encode()
        image = base64.b64decode(encoded)
        imageName = response["imageName"] + '_img_' + format(count) + '.png'

        new_file = os.path.join(new_dir, imageName)

        count += 1

        # saving the images (method 1)
        with open(new_file, "wb") as f:
            f.write(image)

    # respond 'yes' to the command line prompt
    p = os.popen('python manage.py collectstatic', "w")
    p.write("yes")




