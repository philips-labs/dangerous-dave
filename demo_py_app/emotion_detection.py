import cv2
import Algorithmia
import PySimpleGUI as sg
import threading
import _thread

class Captured_frame():
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
class algorithmiaThread (threading.Thread):
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
    client = Algorithmia.client(apiKey)
    algo = client.algo('deeplearning/EmotionRecognitionCNNMBP/1.0.1')
    algo.set_options(timeout=3000)  # optional
    input = frame
    print('Calling algorithmia API')
    res = algo.pipe(input).result
    print('call success\n' + str(res))
    return res

def init_algorithmia(image):
    client = Algorithmia.client(apiKey)
    foo = client.dir("data://.my/data")
    print('image to be saved to disk')
    cv2.imwrite(filename='/tmp/saved_img.jpg', img=frame)
    foo.file("saved_img.jpg").putFile("/tmp/saved_img.jpg")
    print('image saved')
    algo = client.algo('deeplearning/EmotionRecognitionCNNMBP/1.0.1')
    algo.set_options(timeout=3000)  # optional
    input["image"] = "data://.my/data/saved_img.jpg";
    # input["image"] = image
    # print(algo.pipe(input).result)
    # inp = bytearray(open("C:/temp/saved_img.jpg", "rb").read())
    print('Calling algorithmia API')
    res = algo.pipe(input).result
    print('call success\n' + str(res))
    return res

def algo_emo_api_get():
    global emo_result, persons, person, emotions, emotion, emotion_per, current_emotions
    show_res = ''
    emo_result = init_algorithmia_byte(imgbytes)
    persons = emo_result['results']
    for person in persons:
        show_res += '\nPerson' + str(persons.index(person))
        emotions = person['emotions']
        for emotion in emotions:
            if int(emotion['confidence'] * 100) > 1:
                emotion_per = str(emotion['label']) + ' ' + str(int(emotion['confidence'] * 100)) + '%'
                show_res += str('\n' + emotion_per)
    current_emotions = show_res
    print(show_res)
    window['-emo-'].update([show_res])

# Authenticate with Algorithmia API key
apiKey = "fakeKey_put_you_one"

print("Emotion detector started!")

test = True

if test:
    # Initialize computer default camera, grab first frame
    # window = sg.Window('SCD Demo - EmoVideo', [[sg.Image(filename='', key='image')], ], location=(800, 400))
    capture = cv2.VideoCapture(0)
    # ---===--- define the window layout --- #
    current_emotions = ''
    emo_num_display_elem = sg.Text('Emotions: \n{}'.format(current_emotions), size=(15, 30), key='-emo-')
    layout = [[sg.Text('SCD Demo - EmoVideo', size=(10, 1), font='Helvetica 16')],
              [sg.Image(filename='', key='-image-'), emo_num_display_elem],
              [sg.Button('EmoGet', size=(7, 1)),sg.Button('Exit', size=(7, 1), pad=((600, 0), 3), font='Helvetica 14')],
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
    while capture.isOpened():
        event, values = window.read(timeout=0)
        print('fps ' + str(capture.get(cv2.CAP_PROP_FRAME_COUNT)))
        if event in ('Exit', None):
            break
        # Always show available frame in image
        ret, frame = capture.read()
        # print('Frame type is ' + str(type(frame)))
        imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
        image_elem.update(data=imgbytes)
        show_res = ''
        if not ret:  # if out of data stop looping
            break
        elif event in ('EmoGet'):
            print('EmoGet pressed')
            # TODO: need to get the "emo_result = init_algorithmia_byte(imgbytes)" in parallel with video
            try:
                _thread.start_new_thread(algo_emo_api_get,())
            except:
                print("Error: unable to start Algorithmia API thread")
        cur_frame += 1
        # update Text displaying last emotions
        emo_num_display_elem.update('Emotions {}'.format(str(current_emotions)))
    capture.release()
    cv2.destroyAllWindows()
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

            event, values = window.Read(timeout=20, timeout_key='timeout')  # get events for the window with 20ms max wait
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
