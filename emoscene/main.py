import pyautogui
import http.client, urllib.error
import cv2
import ast
import imageio
imageio.plugins.ffmpeg.download()

headers = {
  'Content-Type': 'application/octet-stream',
  'Ocp-Apim-Subscription-Key': '2ea1188254fc4bf1ab8db5a57d87af02',
}
params = urllib.parse.urlencode({    })

before = '1'
trans = 'r'

L10 = 0
R01 = 0


def webcam_realtime():
    cap = cv2.VideoCapture(1)
    cap.set(3,600)
    cap.set(4,400)
    mog = cv2.createBackgroundSubtractorMOG2()

    while True:
        ret, frame = cap.read()
        fgmask = mog.apply(frame)
        if not ret:
            break
        cv2.imwrite('a.jpg', frame)
        body = open('a.jpg', 'rb').read()
        server_io(body)

        sys_frameSwit(fgmask)
        #cv2.imshow('f', frame)
        #cv2.imshow('fs', fgmask)
        k = cv2.waitKey(1)&0xFF
        if k==27:
            break
    cap.release()
    cv2.destroyAllWindows()

def sys_frameSwit(frame):
    global R01, L10,trans
    rr_val = frame[:, int(frame.shape[1] / 8):int(frame.shape[1] / 8)*2].cumsum().max()
    rl_val = frame[:, int(frame.shape[1] / 8)*2:int(frame.shape[1] / 8)*3].cumsum().max()
    lr_val = frame[:, int(frame.shape[1] / 8)*6:int(frame.shape[1] / 8)*7].cumsum().max()
    ll_val = frame[:, int(frame.shape[1] / 8)*7:].cumsum().max()

    l_val = int(ll_val)-int(lr_val)
    r_val = int(rr_val)-int(rl_val)

    k =100000
    p =-20000
    if l_val>k:
        L10 = 1
        print(L10, 0, 0, R01, '::', trans)
    elif l_val<p and L10 is 1:
        print(L10, 1, 0, R01, '::', trans)
        trans = 'l'
        L10 = 0
        R01 = 0
        print(L10, 0, 0, R01, '::', trans)

    if r_val>k:
        R01 = 1
        print(L10, 0, 0, R01, '::', trans)
    elif r_val<p and R01 is 1:
        print(L10, 0, 1, R01, '::', trans)
        trans = 'r'
        L10 = 0
        R01 = 0
        print(L10, 0, 0, R01, '::', trans)

def server_io(body):
    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/emotion/v1.0/recognize?%s" % params, body, headers)

        response = conn.getresponse()
        data = response.read()
        conn.close()
        print(data)
        sys_getEmotion(data)
    except Exception as e:
        pass

def sys_getEmotion(score):
    global before
    utf8 = score.decode("utf-8")
    data_utf8 = ast.literal_eval(utf8)  # string to list conversion
    k = 100000
    anger = int(data_utf8[0]['scores']['anger'] * k)
    contempt = int(data_utf8[0]['scores']['contempt'] * k)
    disgust = int(data_utf8[0]['scores']['disgust'] * k)
    fear = int(data_utf8[0]['scores']['fear'] * k)
    happiness = int(data_utf8[0]['scores']['happiness'] * k)
    neutral = int(data_utf8[0]['scores']['neutral'] * k)
    sadness = int(data_utf8[0]['scores']['sadness'] * k)
    surprise = int(data_utf8[0]['scores']['surprise'] * k)

    print('a:' + str(anger) + ' / c:' + str(contempt) + ' / d:'
          + str(disgust) + ' / f:' + str(fear) + ' / h:' + str(happiness) + ' / n:'
          + str(neutral) + ' / s:' + str(sadness) + ' / r:' + str(surprise))

    lis = [happiness, contempt,fear, surprise, sadness]
    cur = lis.index(max(lis))+1

    if cur != before:
        print(cur)
        pyautogui.press(str(cur))
        pyautogui.press(trans, interval=1)
        before = cur


def main():
    webcam_realtime()

if __name__ == '__main__':
    main()