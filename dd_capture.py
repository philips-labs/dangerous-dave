import cv2 
import Algorithmia
import PySimpleGUI as sg

# Authenticate with Algorithmia API key
apiKey = "fake key, put your key here"

input = {
  "image": "data://deeplearning/example_data/elon_musk.jpg",
  "numResults": 7
}

key = cv2. waitKey(1)
window = sg.Window('Demo Application - OpenCV Integration', [[sg.Image(filename='', key='image')],], location=(800,400))
webcam = cv2.VideoCapture(0)

while True:
    try:
        check, frame = webcam.read()
        cv2.imwrite(filename='/tmp/saved_img.jpg', img=frame)
        #webcam.release()
        img_new = cv2.imread('/tmp/saved_img.jpg', cv2.IMREAD_ANYCOLOR)
        #cv2.imshow("Captured Image", img_new)
        
        cv2.waitKey(500)

        event, values = window.Read(timeout=20, timeout_key='timeout')      # get events for the window with 20ms max wait
        if event is None:  break                                            # if user closed window, quit
 
        client = Algorithmia.client(apiKey)
        foo = client.dir("data://.my/data")
        foo.file("saved_img.jpg").putFile("/tmp/saved_img.jpg")
        algo = client.algo('deeplearning/EmotionRecognitionCNNMBP/1.0.1')
        algo.set_options(timeout=3000) # optional
        input["image"] = "data://.my/data/saved_img.jpg";
        #print(algo.pipe(input).result)        
        #inp = bytearray(open("C:/temp/saved_img.jpg", "rb").read())
        res = algo.pipe(input).result        
        #res = algo.pipe(input).result
        EmoResults = {}
        maxEmotion = 0.7;
        r = res["results"];
        if len(r) > 0:
            print("Found "+ str(len(r)) + " results") 
            for s in r:   
               t = s["bbox"]
               q = s["emotions"]
               bottom = int(t["bottom"])
               top = int(t["top"])
               left = int(t["left"])
               right = int(t["right"])
               start_point = (left, bottom)
               end_point = (right,top)
               blue = (255, 0, 0)
               green = (0, 255, 0)
               red = (0,0,255) 
               thickness = 1
 
           #print (s["emotions"])
               for emotions in q:
                       #print(emotions)
                       if float(emotions["confidence"]) > maxEmotion:
                           print(emotions["label"] + "=" + str(emotions["confidence"]))
                           if emotions["label"] == "Angry" :
                               print ("Watchout !!!!!   Dangerous Dave......")
                               #emoResults[emotions.attribute] = emotions.value;
                               cv2.rectangle(img_new, start_point, end_point, red, thickness)   
                               cv2.putText(img_new, emotions["label"], (right+10, top), 0, 0.6, red)
                           else: 
                               cv2.rectangle(img_new, start_point, end_point, green, thickness)   
                               cv2.putText(img_new, emotions["label"], (right+10, top), 0, 0.6, green)
                           
                           #cv2.imwrite("c:/temp/ttt.jpg", img_new)
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
    

