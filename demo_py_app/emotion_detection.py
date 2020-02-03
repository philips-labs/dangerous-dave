import cv2
import Algorithmia
import PySimpleGUI as sg
import io
from PIL import Image, ImageTk
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

def get_image_data(capture, first=False):
    if (capture.isOpened()):
        ret, frame = capture.read()
    else:
        return False, ''
    #ret, frame = capture.read()
    frame = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return ret, bio.getvalue()
    return ret, ImageTk.PhotoImage(image=img)

def get_img_data(f, maxsize=(1200, 850), first=False):
    """Generate image data using PIL
    """
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)

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

def live_video3(cap):
    global frame
    # cap = cv2.VideoCapture(camera_port)
    if (cap.isOpened()):
        return cap.read()
        ret, frameNow = cap.read()

        if not ret:
            cv2.waitKey(1)
            return ''
        else:
            return frameNow
            # cv2.imshow('Video', frameNow)
            frame = frameNow
            return cv2.imshow('Video', frameNow)
        # if cv2.waitKey(75) & 0xFF == ord('q'):
        #     break
    # cap.release()
    # cv2.destroyAllWindows()

# Authenticate with Algorithmia API key
apiKey = "siml7JQGhnZ+g4QrXf07OdzK7xJ1"

input = {
    "image": "data://deeplearning/example_data/elon_musk.jpg",
    "numResults": 7
}

print("Emotion detector started!")

test = True


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


if test:
    gui_show = False
    video_option = 2

    # Initialize computer default camera, grab first frame
    # window = sg.Window('SCD Demo - EmoVideo', [[sg.Image(filename='', key='image')], ], location=(800, 400))
    capture = cv2.VideoCapture(0)
    # ---===--- define the window layout --- #
    if video_option == 2:
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



    if video_option == 1:
        # captured, frame = get_image_data(capture, first=True)
        # print('Frame type is ' + str(type(frame)))

        # if captured:
        #     image_elem = sg.Image(data=frame)
        # else: # get from temp first frame until camera is opened and producing frames
        #     filename = '/tmp/saved_img.jpg'
        #     image_elem = sg.Image(data=get_img_data(filename, first=True))
        image_elem = sg.Image(filename='', key='-image-')
        frame_names = ['Emotions:'] # TODO: when object for every frame is introduce, we can move the saved object here for review later
        num_emotions = len(frame_names)-1
        filename_display_elem = sg.Text('captured0', size=(80, 3))
        emo_num_display_elem = sg.Text('Emotions: \n{}'.format(num_emotions), size=(15, 30))

        # define layout, show and read the form
        col = [[filename_display_elem],
               [image_elem]]

        col_files = [[sg.Listbox(values=frame_names, change_submits=True, size=(60, 30), key='listbox')],
                     [sg.Button('Next', size=(8, 2)), emo_num_display_elem]]

        layout = [[sg.Column(col_files), sg.Column(col)]]

        window = sg.Window('SCD Demo - EmoVideo', layout, return_keyboard_events=True,
                           location=(0, 0), use_default_focus=False)
        image_elem = window['-image-']

        while capture.isOpened():
            # read the form
            #event, values = window.read() # Capture and show frame only on Next button, or any other event from Window(but there are none for now)
            event, values = window.Read(timeout=0, timeout_key='timeout')  # get events for the window with 20ms max wait
            print(event, values)
            # update window with new image
            captured, frame = get_image_data(capture, first=True)
            print('Frame type is ' + str(type(frame)))
            # imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            #image_elem.update(data=imgbytes)
            if captured:
                image_elem.update(data=frame)
            # perform button and keyboard operations
            show_res = ''
            if event is None:
                break
            elif event in ('Next'):
                print('Next pressed')
                emo_result = init_algorithmia_byte(frame)
                persons = emo_result['results']
                for person in persons:
                    show_res += '\nPerson' + str(persons.index(person))
                    emotions = person['emotions']
                    for emotion in emotions:
                        if int(emotion['confidence'] * 100) > 1:
                            emotion_per = str(emotion['label']) + ' ' + str(int(emotion['confidence'] * 100)) + '%'
                            frame_names.append(emotion_per)
                            show_res += str('\n' + emotion_per)
                filename = show_res
                print(show_res)
                num_emotions = show_res
                #
                window['listbox'].update([show_res])
            elif event == 'listbox':  # something from the listbox, TODO:saved objects list, change image and emotions
                print('Somebody touched listbox. Do not use it for now')
                # f = values["listbox"][0]  # selected filename
                # filename = ImageTk.PhotoImage(frame)  # read this file
                # i = frame_names.index(f)  # update running index
            else:
                filename = '/tmp/saved_img.jpg'

            filename_display_elem.update(filename)
            # update page display
            emo_num_display_elem.update('Emotions {}'.format(str(num_emotions)))

        capture.release()
        cv2.destroyAllWindows()
        window.close()




    if gui_show:
        try:
            image_disp = ''
            frame = ''
            sg.theme('BluePurple')

            layout = [\
                # [sg.Image(frame, size=(800, 400), key='-OUTPUT-')], \
                [sg.Text('                               ', size=(10, 20), font=('Helvetica', 20), justification='left', key='_OUTPUT_TEXT_')],
                      [sg.Button('Show'), sg.Button('Exit')]]

            window = sg.Window('SCD Demo - EmoVideo', layout)
            print('Window created for gui')
            cap = cv2.VideoCapture(0)

            while True:  # Event Loop
                event, values = window.read()
                # window['-OUTPUT-'].update(frame)
                # event, values = window.Read(timeout=20, timeout_key='timeout')  # get events for the window with 20ms max wait
                print(" Event was " + str(event) + " with value " + str(values))
                image_disp = live_video3(cap)

                if event in ('Exit'): # if user closed window, quit
                    cap.release()
                    cv2.destroyAllWindows()
                    break
                if event == 'Show':
                    # cap = cv2.VideoCapture(0)
                    print('aquire image from camera')
                    image_disp = live_video3(cap)
                    #image_disp = frame
                    # Update the "output" text element to be the value of "input" element
                    print('Get emotions')
                    emo_result = init_algorithmia(image_disp)
                    # print('Emotions \n' + emo_result)
                    show_res = ''
                    for i in range(0, 6):
                        if int(emo_result['results'][0]['emotions'][i]['confidence'] * 100) > 1:
                            show_res += str('\n' + emo_result['results'][0]['emotions'][i]['label']) + ' ' + str(int(emo_result['results'][0]['emotions'][i]['confidence']*100)) +'%'
                    window['_OUTPUT_TEXT_'].update(show_res)
                    # print('waitinig new event')
        except:
            window.close()
            print("Turning off camera.")
            # webcam.release()
            print("Camera off.")
            print("Program ended.")
            cv2.destroyAllWindows()
            # break
    #print("I am ending tested code!")
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