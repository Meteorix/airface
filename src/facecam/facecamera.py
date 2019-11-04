# coding=utf-8
from kivy.utils import platform
IS_ANDROID = platform == "android"
from kivy.uix.camera import Camera
from kivy.properties import ListProperty
from facecam.boundingbox import BoundingBox
if IS_ANDROID:
    from facecam.fixedcamera import CameraAndroidFixed as CameraCore
else:
    from kivy.core.camera import Camera as CameraCore

from PIL import Image, ImageOps
import numpy as np
import os
import cv2

this_dir = os.path.dirname(os.path.abspath(__file__))
xml_path = os.path.join(this_dir, "./haarcascade_frontalface_default.xml")
detector = cv2.CascadeClassifier(xml_path)


class FaceCamera(Camera):
    """
    Subclass of the Kivy camera class with support for realtime face detection.
    """

    detected_faces = ListProperty([])
    '''
    List with the names of the currently detected faces.
    '''

    face_locations = ListProperty([])
    '''
    List of locations of the currently detected faces. The coordinates are 
    relative to the texture size.
    '''

    def __init__(self, *args, **kwargs):
        super(FaceCamera, self).__init__(*args, index=1, **kwargs)
        self._fix_angle = [-90, 90][self.index] if IS_ANDROID else 0

        self._known_faces = []
        self._known_names = []

        # bounding boxes for each face
        self._bounding_boxes = []

    def _on_index(self, *largs):
        self._camera = None
        if self.index < 0:
            return
        if self.resolution[0] < 0 or self.resolution[1] < 0:
            return
        self._camera = CameraCore(index=self.index, resolution=self.resolution, stopped=True)
        self._camera.bind(on_load=self._camera_loaded)
        if self.play:
            self._camera.start()
            self._camera.bind(on_texture=self.on_tex)

    def on_tex(self, cam):
        super(FaceCamera, self).on_tex(cam)

        # down scale factor for the image to speed up face detection
        scale = 2
        # get texture from camera object and create a pillow image
        # from the raw data
        tex = cam.texture

        im = Image.frombytes('RGBA', tex.size, tex.pixels, 'raw')
        im_w, im_h = tex.width//scale, tex.height//scale
        im = im.resize((im_w, im_h))
        im = fix_android_image(im)
        # convert image to np.array without alpha channel
        arr = np.array(im)[:, :, :3]
        # get face locations from the resized image
        gray = cv2.cvtColor(arr, cv2.COLOR_BGRA2GRAY)
        loc = detector.detectMultiScale(gray, 1.3, 5)
        # print(loc)

        if isinstance(loc, tuple) or not loc.any():
            faces = []
            locations = []
        else:
            faces = ["Unknown"] * len(loc)
            locations = loc

        # sort faces array and location array based on the name of face
        indices = np.argsort(faces)
        self.detected_faces = [f for f, i in sorted(zip(faces, indices), key=lambda e: e[1])]
        self.face_locations = [(v*scale for v in l) for l, i in sorted(zip(locations, indices), key=lambda e: e[1])]

    def on_detected_faces(self, camera, faces):
        """
        Called when the detected faces change.
        :param camera: instance of this class
        :param faces: array containing the name of each face
        """
        # remove old bounding boxes
        for bbox in self._bounding_boxes:
            self.remove_widget(bbox)
        self._bounding_boxes = []

        # add bounding boxes for each face
        for face_name in faces:
            bbox = BoundingBox(name=face_name, size_hint=(None, None))
            self._bounding_boxes.append(bbox)
            self.add_widget(bbox)

    def on_face_locations(self, camera, locations):
        """
        Called when the location of the faces change. The location for each face
        is give by (top, right, bottom, left) coordinates relative to the
        cameras texture.
        :param camera: instance of this class
        :param locations: array with new locations for each face
        """
        # fix the position of the rectangle
        for loc, bbox in zip(locations, self._bounding_boxes):
            # calculate texture size and actual image size
            rw, rh = self.texture.size
            nw, nh = self.norm_image_size
            # calculate scale factor caused by allow_stretch=True and/or keep_ratio = False
            sw, sh = nw/rw, nh/rh

            anchor_l = self.center[0]-nw/2
            anchor_t = self.center[1]+nh/2

            # calculate position of the face
            x, y, w, h = loc

            t = int(anchor_t - y*sh)
            b = int(anchor_t - (y+h)*sh)
            r = int(anchor_l + x*sw)
            l = int(anchor_l + (x+w)*sw)

            # update bounding box
            bbox.rotate_angle = -1 * self._fix_angle
            bbox.rotate_center = self.center
            bbox.pos = (int(l), int(b))
            bbox.size = (int(r-l), int(t-b))


def fix_android_image(pil_image):
    """
    On Android, the image seems mirrored and rotated somehow, refs #32.
    """
    if not IS_ANDROID:
        return pil_image
    pil_image = pil_image.rotate(90)
    pil_image = ImageOps.mirror(pil_image)
    return pil_image
