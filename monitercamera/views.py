

from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from .forms import InquiryForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
import cv2
from django.http import StreamingHttpResponse
from django.shortcuts import render
from myproject.settings import BASE_DIR
import datetime
import time


'''
ファーストビュー
'''
class IndexView(generic.TemplateView):
    template_name = "index.html"


'''
お問い合わせフォーム
'''
class InquiryView(generic.FormView):
    template_name = "inquiry.html"
    form_class = InquiryForm
    success_url = reverse_lazy('diary:inquiry')

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'メッセージを送信しました')
        return super().form_valid(form)


'''
ログイン後ページ
'''
class CameraView(LoginRequiredMixin, generic.TemplateView):
    def get(self, request):
        return render(request, 'camera.html', {})


'''
カメラのリアルタイム表示
'''
class CameraVideoView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'camera_video.html'


'''
ストリーミング画像を定期的に返却するview
'''
def videoView():
    return lambda _: StreamingHttpResponse(generate_frame(), content_type='multipart/x-mixed-replace; boundary=frame')

'''
フレーム生成・返却する処理
'''

def generate_frame():
    capture = cv2.VideoCapture(0)

    anterior = 0
    shot_dense = 0.5
    considerable_frames = 20
    prev_faces = []
    prev_shot = None
    count=0

    #フレーム数カウント用
    while True:
        if not capture.isOpened():
            print("Capture is not opened.")
            break
        # 動画ストリームからフレームを取得
        success, image = capture.read()
        cascade_path = str(BASE_DIR) + '/facedetect_features/haarcascade_frontalface_default.xml'
        gry = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(cascade_path)
        facerect = cascade.detectMultiScale(gry, 1.5, 2)
        rectange_color = (255,0,0)

        # 顔が検出されるたびに連続で撮影されないための工夫
        if prev_shot is None or (datetime.datetime.now() - prev_shot).seconds > 3:
            for rect in facerect:
                cv2.rectangle(image,tuple(rect[0:2]),tuple(rect[0:2]+rect[2:4]), rectange_color, thickness=2)
            prev_faces.append(len(facerect))
            if len(prev_faces) > considerable_frames:
                    drops = len(prev_faces) - considerable_frames
                    # prev_facesのリストの先頭からdrops分だけ要素を削除したlistを返す
                    # prev_facesは常に20の要素数を保つ
                    prev_faces = prev_faces[drops:]
            # その20の要素数のうち、0以上の数が全要素数(=20)のどれくらいの割合を占めるかチェック
            dense = sum([1 for i in prev_faces if i > 0]) / float(len(prev_faces))

            # prev_facesに20よりも多くの要素が格納されようとしたとき
            if len(prev_faces) >= considerable_frames and dense >= shot_dense:
                save_fig_name = './static/assets/img/IMG{}.jpg'.format(count)
                count += 1
                cv2.imwrite(save_fig_name, image)

                prev_faces = []
                prev_shot = datetime.datetime.now()

        ret, jpeg = cv2.imencode('.jpg', image)
        byte_frame = jpeg.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + byte_frame + b'\r\n\r\n')
    capture.release()


'''
カメラの写真表示
'''
class CameraPhotoView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'camera_photo.html'



