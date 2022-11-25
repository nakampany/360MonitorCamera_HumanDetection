
import logging
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from .forms import InquiryForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
import cv2
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.views import View
from myproject.settings import BASE_DIR


logger = logging.getLogger(__name__)

class IndexView(generic.TemplateView):
    template_name = "index.html"

class InquiryView(generic.FormView):
    template_name = "inquiry.html"
    form_class = InquiryForm
    success_url = reverse_lazy('diary:inquiry')

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'メッセージを送信しました')
        logger.info('inquiry sent by {}'.format(form.cleaned_data['name']))
        return super().form_valid(form)


class CameraPhotoView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'camera_photo.html'


class CameraView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'camera.html', {})

# ストリーミング画像を定期的に返却するview
def video_feed_view():
    return lambda _: StreamingHttpResponse(generate_frame(), content_type='multipart/x-mixed-replace; boundary=frame')

# フレーム生成・返却する処理
def generate_frame():
    capture = cv2.VideoCapture(0)

    while True:
        if not capture.isOpened():
            print("Capture is not opened.")
            break
        # カメラからフレーム画像を取得
        success, image = capture.read()

        cascade_path = str(BASE_DIR) + "/haarcascade_frontalface_default.xml"
        print(cascade_path)
        gry = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(cascade_path)
        facerect = cascade.detectMultiScale(gry, 1.5, 2)
        rectange_color = (255,0,0)
        if len(facerect) > 0:
            for rect in facerect:
                cv2.rectangle(image,tuple(rect[0:2]),tuple(rect[0:2]+rect[2:4]),rectange_color,thickness=2)

        ret, jpeg = cv2.imencode('.jpg', image)
        byte_frame = jpeg.tobytes()

        # フレーム画像のバイナリデータをユーザーに送付する
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + byte_frame + b'\r\n\r\n')
    capture.release()


