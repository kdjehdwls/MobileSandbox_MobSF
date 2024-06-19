### 프리다(Frida)는 다이나믹 인스트루멘테이션(dynamic instrumentation) 툴로, 실행 중인 애플리케이션에 코드를 삽입하여 그 동작을 변경하거나 추적할 수 있게 해주는 도구

---

### 아키텍쳐 확인
**adb shell getprop ro.product.cpu.abi**

x86

---

맞는 아키텍쳐 **server** 찾아서 다운 / core 아님

https://github.com/frida/frida/releases

---

프리다 서버 넣기

**adb push frida-server-16.2.1-android-x86 /data/local/tmp**

---

권한주기

C:\Users\HP\Downloads>**adb shell**

vbox86p:/ # **su**

vbox86p:/ # **chmod 755 /data/local/tmp/frida-server-16.2.1-android-x86**

---

실행

vbox86p:/ # **/data/local/tmp/frida-server-16.2.1-android-x86 &**

[1] 3293   //1은 작업번호 3293은 pid

---

연결 프로세스 확인

C:\Users\HP>**frida-ps -U**

PID  Name

...

2753  Calendar
2822  Clock
2730  Email
2542  Google Play Store

…
3293  frida-server-16.2.1-android-x86

---

패키지 확인

**adb shell pm list packages**

**adb shell pm list packages | findstr heBb** (윈도우,리눅스는 grep?)

com.ldjSxw.heBbQd

---

스크립트 주입해서 실행

**frida -U -l "bypass_script.js" -f "com.ldjSxw.heBbQd"**

`frida -U -n "My Scan APP" -l frida_script.js`

- **`*U`**: USB 장치에 연결된 기기를 대상으로 합니다. 일반적으로 모바일 디바이스에서 Frida 서버가 실행 중일 때 사용됩니다.*
- 
- **`*l <script>`**: Frida 스크립트 파일을 지정합니다. 이 스크립트는 대상 프로세스에 주입되어 실행됩니다.*
- 
- **`*f <package-name|path>`**: 지정된 패키지 또는 앱을 시작하고 해당 프로세스에 스크립트를 주입합니다. 앱이 이미 실행 중이면 종료되고 다시 시작됩니다.*
- 
- **`*n <process-name>`**: 이미 실행 중인 프로세스의 이름을 지정하여, 해당 프로세스에 스크립트를 주입합니다.*
- 
- **`*p <pid>`**: 프로세스 ID를 직접 지정하여 해당 프로세스에 스크립트를 주입합니다.*
- 
- **`*D <device-id>`**: 연결할 대상 디바이스의 ID를 지정합니다. 여러 디바이스가 연결된 경우 유용합니다.*


---

//

삭제명령어 

rm -r /path/to/your/directory

---

activity 확인

C:\Users\HP>adb shell dumpsys package com.ldjSxw.heBbQd | findstr -i activity

Activity Resolver Table:

e6f04 com.ldjSxw.heBbQd/.ScanActivity filter 7ca4cf5

d10aced com.ldjSxw.heBbQd/.IntroActivity filter 6f9ea2c
