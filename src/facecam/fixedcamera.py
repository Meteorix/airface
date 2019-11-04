# coding=utf-8
from jnius import autoclass
from kivy.core.camera.camera_android import CameraAndroid
from kivy.graphics.texture import Texture
from kivy.graphics import Fbo, Callback, Rectangle
Camera = autoclass('android.hardware.Camera')
SurfaceTexture = autoclass('android.graphics.SurfaceTexture')
GL_TEXTURE_EXTERNAL_OES = autoclass('android.opengl.GLES11Ext').GL_TEXTURE_EXTERNAL_OES
ImageFormat = autoclass('android.graphics.ImageFormat')


class CameraAndroidFixed(CameraAndroid):
    def init_camera(self):
        self._release_camera()
        self._android_camera = Camera.open(self._index)
        params = self._android_camera.getParameters()
        width, height = self._resolution
        params.setPreviewSize(width, height)
        # params.setFocusMode('continuous-picture')
        self._android_camera.setParameters(params)
        # self._android_camera.setDisplayOrientation()
        self.fps = 30.

        pf = params.getPreviewFormat()
        assert(pf == ImageFormat.NV21)  # default format is NV21
        self._bufsize = int(ImageFormat.getBitsPerPixel(pf) / 8. *
                            width * height)

        self._camera_texture = Texture(width=width, height=height,
                                       target=GL_TEXTURE_EXTERNAL_OES,
                                       colorfmt='rgba')
        self._surface_texture = SurfaceTexture(int(self._camera_texture.id))
        self._android_camera.setPreviewTexture(self._surface_texture)

        self._fbo = Fbo(size=self._resolution)
        self._fbo['resolution'] = (float(width), float(height))
        self._fbo.shader.fs = '''
            #extension GL_OES_EGL_image_external : require
            #ifdef GL_ES
                precision highp float;
            #endif
            /* Outputs from the vertex shader */
            varying vec4 frag_color;
            varying vec2 tex_coord0;
            /* uniform texture samplers */
            uniform sampler2D texture0;
            uniform samplerExternalOES texture1;
            uniform vec2 resolution;
            void main()
            {
                vec2 coord = vec2(tex_coord0.y * (
                    resolution.y / resolution.x), 1. -tex_coord0.x);
                gl_FragColor = texture2D(texture1, tex_coord0);
            }
        '''
        with self._fbo:
            self._texture_cb = Callback(lambda instr:
                                        self._camera_texture.bind)
            Rectangle(size=self._resolution)
