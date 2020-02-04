import cv2
import Algorithmia
import PySimpleGUI as sg
import threading
import _thread
import time


# Authenticate with Algorithmia API key
apiKey = "PLEASEE add your Algorithmia API key" 

class PersonInImage:
    pass


class CapturedFrame():
    def __init__(self, image, name):
        self.name = name
        self.image = image
        self.emotions = []
        self.binary = ''
        self.status = 'init'

    def __str__(self):
        s = "Name: " + self.name
        s += " Status: " + str(self.health)
        return s

    def grab(self, item):
        self.inventory.append(item)

    def get_health(self):
        while (capture.isOpened()):
            self.status = 'capture_mode'
        return self.health


# Still not used
class algorithmiaThread(threading.Thread):
    def __init__(self, threadID, name, frame):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.frame = frame

    def run(self):
        print("Starting " + self.name)
        # Get lock to synchronize threads
        # threadLock.acquire()
        init_algorithmia_byte(frame)
        # Free lock to release next thread
        # threadLock.release()


def init_algorithmia_byte(frame):
    client_algorithmia = Algorithmia.client(apiKey)
    algo_emo_rocognition = client_algorithmia.algo('deeplearning/EmotionRecognitionCNNMBP/1.0.1')
    algo_emo_rocognition.set_options(timeout=3000)  # optional
    input_byte_image = frame
    print('Calling algorithmia API')
    res = algo_emo_rocognition.pipe(input_byte_image).result
    print('call success\n' + str(res))
    return res


def init_algorithmia(image):
    client_algorithmia = Algorithmia.client(apiKey)
    local_data_dir = client_algorithmia.dir("data://.my/data")
    print('image to be saved to disk')
    cv2.imwrite(filename='/tmp/saved_img.jpg', img=frame)
    local_data_dir.file("saved_img.jpg").putFile("/tmp/saved_img.jpg")
    print('image saved')
    algorithm_emo_reckogniton = client_algorithmia.algo('deeplearning/EmotionRecognitionCNNMBP/1.0.1')
    algorithm_emo_reckogniton.set_options(timeout=3000)  # optional
    input["image"] = "data://.my/data/saved_img.jpg";
    print('Calling algorithmia API')
    results_emotion_recognition = algorithm_emo_reckogniton.pipe(input).result
    print('call success\n' + str(results_emotion_recognition))
    return results_emotion_recognition


def algorithmia_emo_api_get(faces_crop_ind):
    global current_emotions, window
    show_emo_res = ''
    emo_result = init_algorithmia_byte(faces_crop_ind[0])
    persons = emo_result['results']
    for person in persons:
        show_emo_res += '\nPerson ' + str(faces_crop_ind[1]+1)
        emotions_algorithm_array = person['emotions']
        for emotion in emotions_algorithm_array:
            if int(emotion['confidence'] * 100) > 1:
                emotion_per = str(emotion['label']) + ' ' + str(int(emotion['confidence'] * 100)) + '%'
                show_emo_res += str('\n' + emotion_per)
    current_emotions += show_emo_res
    print(show_emo_res)
    window['-emo-'].update([current_emotions])


def face_detect(image):  # input is cv2.image -> cv2.imread('my_image.jpg'):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);
    haar_cascade_face = cv2.CascadeClassifier(
        'haarcascade_frontalface_default.xml')  # loading the classifier for frontal face
    faces_rects = haar_cascade_face.detectMultiScale(image_gray, scaleFactor=1.2, minNeighbors=5);
    print('Faces found: ', len(faces_rects))
    return faces_rects


print("Emotion detector started!")

test = True

if test:
    # Initialize computer default camera, grab first frame
    capture = cv2.VideoCapture(0)
    # ---===--- define the window layout --- #
    current_emotions = ''
    emo_num_display_elem = sg.Text('Emotions: \n{}'.format(current_emotions), size=(15, 30), key='-emo-')
    layout = [[sg.Text('SCD Demo - EmoVideo', size=(10, 1), font='Helvetica 16')],
              [sg.Image(filename='', key='-image-'), emo_num_display_elem],
              [sg.Button('EmoGet', size=(7, 1)),
               sg.Button('Exit', size=(7, 1), pad=((600, 0), 3), font='Helvetica 14')],
              ]

    # create the window and show it without the plot
    window = sg.Window('Demo Application - Video and Emodetection Integration',
                       layout,
                       no_titlebar=False,
                       location=(0, 0))

    # locate the elements we'll be updating. Does the search only 1 time
    image_elem = window['-image-']

    # ---===--- LOOP through video file by frame --- #
    cur_frame = 0
    #
    t = time.time()
    while capture.isOpened():
        # print('Event time: {}'.format(t-time.time()))
        # t = time.time()
        event, values = window.read(timeout=0)
        # print('fps ' + str(capture.get(cv2.CAP_PROP_FRAME_COUNT)))
        if event in ('Exit', None):
            break
        # Always show available frame in image
        ret, frame = capture.read()
        faces_rectangles = face_detect(frame)
        faces_crop = []
        for (x, y, w, h) in faces_rectangles:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            faces_crop.append(frame[y:y + h, x:x + w, :])
        imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
        image_elem.update(data=imgbytes)
        show_res = ''
        if not ret:  # if out of data stop looping
            break
        elif event in 'EmoGet':
            current_emotions = ''
            print('EmoGet pressed for {} faces'.format(len(faces_crop)))
            try:
                for crop_face in faces_crop:
                    face_ind = [cv2.imencode('.png', crop_face)[1].tobytes(), faces_crop.index(crop_face)]
                    _thread.start_new_thread(algorithmia_emo_api_get, (face_ind,))
            except:
                print("Error: unable to start Algorithmia API thread")
        cur_frame += 1
        # update Text displaying last emotions
        emo_num_display_elem.update('Emotions {}'.format(str(current_emotions)))
    capture.release()
    cv2.destroyAllWindows()
    print('Event time: {}'.format(time.time()-t))
    print('Frames for this time: {}'.format(cur_frame))
    print('Average FPS: {}'.format(cur_frame/(time.time()-t)))
    window.close()

else:
    key = cv2.waitKey(1)
    window = sg.Window('SCD Demo - EmoVideo', [[sg.Image(filename='', key='image')], ], location=(800, 400))
    webcam = cv2.VideoCapture(0)

    while True:
        try:
            check, frame = webcam.read()
            cv2.imwrite(filename='/tmp/saved_img.jpg', img=frame)
            # webcam.release()
            img_new = cv2.imread('/tmp/saved_img.jpg', cv2.IMREAD_ANYCOLOR)
            # cv2.imshow("Captured Image", img_new)

            cv2.waitKey(500)

            event, values = window.Read(timeout=20,
                                        timeout_key='timeout')  # get events for the window with 20ms max wait
            if event is None:  break  # if user closed window, quit

            client = Algorithmia.client(apiKey)
            foo = client.dir("data://.my/data")
            foo.file("saved_img.jpg").putFile("/tmp/saved_img.jpg")
            algo = client.algo('deeplearning/EmotionRecognitionCNNMBP/1.0.1')
            algo.set_options(timeout=3000)  # optional
            input["image"] = "data://.my/data/saved_img.jpg";
            # print(algo.pipe(input).result)
            # inp = bytearray(open("C:/temp/saved_img.jpg", "rb").read())
            res = algo.pipe(input).result
            # res = algo.pipe(input).result
            EmoResults = {}
            maxEmotion = 0.7;
            r = res["results"];
            if len(r) > 0:
                print("Found " + str(len(r)) + " results")
                for s in r:
                    t = s["bbox"]
                    q = s["emotions"]
                    bottom = int(t["bottom"])
                    top = int(t["top"])
                    left = int(t["left"])
                    right = int(t["right"])
                    start_point = (left, bottom)
                    end_point = (right, top)
                    blue = (255, 0, 0)
                    green = (0, 255, 0)
                    red = (0, 0, 255)
                    thickness = 1

                    # print (s["emotions"])
                    for emotions in q:
                        # print(emotions)
                        if float(emotions["confidence"]) > maxEmotion:
                            print(emotions["label"] + "=" + str(emotions["confidence"]))
                            if emotions["label"] == "Angry":
                                print("Watchout !!!!!   Dangerous Dave......")
                                # emoResults[emotions.attribute] = emotions.value;
                                cv2.rectangle(img_new, start_point, end_point, red, thickness)
                                cv2.putText(img_new, emotions["label"], (right + 10, top), 0, 0.6, red)
                            else:
                                cv2.rectangle(img_new, start_point, end_point, green, thickness)
                                cv2.putText(img_new, emotions["label"], (right + 10, top), 0, 0.6, green)

                            # cv2.imwrite("c:/temp/ttt.jpg", img_new)
                cv2.imshow("Captured Image", img_new)

            key = cv2.waitKey(1)
            if key == ord('q'):
                print("Turning off camera.")
                webcam.release()
                print("Camera off.")
                print("Program ended.")
                cv2.destroyAllWindows()
                break

        except(KeyboardInterrupt):
            print("Turning off camera.")
            webcam.release()
            print("Camera off.")
            print("Program ended.")
            cv2.destroyAllWindows()
            break
