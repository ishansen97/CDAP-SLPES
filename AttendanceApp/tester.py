import cv2
from .faceRecognition import faceDetection, train_classifier, labels_for_training_data, draw_rect, put_text


#This module takes images  stored in diskand performs face recognition
test_img=cv2.imread('TestImages/frame0.jpg')#test_img path
faces_detected,gray_img=faceDetection(test_img)
print("faces_detected:",faces_detected)


#Comment belows lines when running this program second time.Since it saves training.yml file in directory
faces,faceID=labels_for_training_data('trainingImages')
face_recognizer=train_classifier(faces,faceID)
face_recognizer.write('trainingData.yml')


# For subsequent runs
face_recognizer=cv2.face.LBPHFaceRecognizer_create()
face_recognizer.read('trainingData.yml')#use this to load training data for subsequent runs

name={0: "IT17138000", 1: "IT17100908", 2: "IT17098960"}#creating dictionary containing names for each label
file = open("attendance.txt", "w")

for face in faces_detected:
    (x,y,w,h)=face
    roi_gray=gray_img[y:y+h,x:x+h]
    label,confidence=face_recognizer.predict(roi_gray)#predicting the label of given image
    print("confidence:",confidence)
    print("label:",label)
    draw_rect(test_img,face)
    predicted_name=name[label]
    if(confidence>90):#If confidence more than 37 then don't print predicted face text on screen
        continue
    file.write(predicted_name)
    put_text(test_img,predicted_name,x,y)
file.close()
resized_img=cv2.resize(test_img,(700,700))
cv2.imshow("face dtecetion tutorial",resized_img)
cv2.waitKey(0)#Waits indefinitely until a key is pressed
cv2.destroyAllWindows





