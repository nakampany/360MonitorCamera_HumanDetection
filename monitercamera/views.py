
import logging
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from .forms import InquiryForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404


logger = logging.getLogger(__name__)


class InquiryView(generic.FormView):
    template_name = "inquiry.html"
    form_class = InquiryForm
    success_url = reverse_lazy('diary:inquiry')

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'メッセージを送信しました')
        logger.info('inquiry sent by {}'.format(form.cleaned_data['name']))
        return super().form_valid(form)

class CameraView(LoginRequiredMixin, generic.TemplateView):
    template_name = "camera.html"

class CameraPhotoView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'camera_photo.html'



import cv2
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.views import View


# ストリーミング画像・映像を表示するview
class IndexView(generic.TemplateView):

    def get(self, request):
        return render(request, 'index.html', {})

# ストリーミング画像を定期的に返却するview
def video_feed_view():
    return lambda _: StreamingHttpResponse(generate_frame(), content_type='multipart/x-mixed-replace; boundary=frame')

# フレーム生成・返却する処理
def generate_frame():
    capture = cv2.VideoCapture(0)  # USBカメラから

    while True:
        if not capture.isOpened():
            print("Capture is not opened.")
            break
        # カメラからフレーム画像を取得
        ret, frame = capture.read()
        if not ret:
            print("Failed to read frame.")
            break
        # フレーム画像バイナリに変換
        ret, jpeg = cv2.imencode('.jpg', frame)
        byte_frame = jpeg.tobytes()
        # フレーム画像のバイナリデータをユーザーに送付する
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + byte_frame + b'\r\n\r\n')
    capture.release()