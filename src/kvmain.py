# coding=utf-8
"""
本文件是AirPort加载python代码的入口文件
文件路径一定放在手机: /sdcard/kv/kvmain.py
"""
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty

from facecam import FaceCamera


Builder.load_string('''

<CameraClick>:
    face_camera: camera
    orientation: 'vertical'

    FaceCamera:
        id: camera
        pos: self.x, dp(48)
        height: root.height - dp(48)
        center: self.size and root.center
        allow_stretch: True
        keep_ratio: True
        resolution: [640, 480]
        play: False
        canvas.before:
            PushMatrix
            Rotate:
                angle: self._fix_angle
                origin: self.center
        canvas.after:
            PopMatrix

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: '48dp'

        ToggleButton:
            text: 'Play'
            state: 'down'
            on_press:
                camera.play = not camera.play
                self.text = 'Pause' if self.text == 'Play' else 'Play'

        Button:
            text: 'Capture'
            on_press: root.capture()
''')


class CameraClick(FloatLayout):

    camera = ObjectProperty()
    '''
    Reference to camera instance.
    '''

    def capture(self):
        """
        Function to capture the images and give them the names
        according to their captured time and date.
        """
        self.camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        self.camera.export_to_png("IMG_{}.png".format(timestr))
        print("Captured")


class TestCamera(App):

    def build(self):
        return CameraClick()


TestCamera().run()
