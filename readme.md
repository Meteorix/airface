AirFace
========

用Python+Kivy实现的安卓开发新姿势，简单几步实现一个人脸识别的App，配合公众号文章使用。

欢迎关注我的个人公众号`Meteorix`

![qrcode](./qrcode.bmp)


# development

`kvmain.py`是加载python代码的入口文件。
文件路径一定放在手机`/sdcard/kv/kvmain.py`。

```shell
# install the apk
adb install -t airport.apk

# 在手机中开启airport应用的相机权限

# prepare sdcard
adb shell mkdir -p /sdcard/kv

# update python scripts
adb push src/* /sdcard/kv/

# restart app
adb shell am force-stop "org.airtest.airpot" && \
adb shell am start -n "org.airtest.airport/org.kivy.android.PythonActivity"
```

# Python Interactive Shell

不放`kvmain.py`或者代码报错的时候，会显示本机的ssh地址。
照着显示的ssh命令，可以无线连接手机上的python终端。

或者你也可以用以下adb指令连接ssh端口

```shell
adb forward tcp:6060 tcp:6060
ssh -p 6060 admin@127.0.0.1
```

**注意**：ssh登陆密码是作者的github用户名小写。

# FaceCam App

### run app on desktop
```shell
cd scripts
python cam.py
```

### run app on android
follow the steps in [development](#development)
