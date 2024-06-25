# MobileSandbox_MobSF
**샌드박스 구축을 통한 악성코드 자동 탐지 및 분석 시스템 개발**

**1. 환경설정**

- MobSF 설치 (https://github.com/MobSF/Mobile-Security-Framework-MobSF)
- Android studio & app tools 설치 (https://developer.android.com/studio)
- SDK 컴포넌트 설치
- Emulator(genemotion) 설치 (https://www.genymotion.com/)
- Python3 (https://www.python.org/downloads/)
- openssl (https://slproweb.com/products/Win32OpenSSL.html)
- visual studio build-tools (https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16)
- JDK(11) (https://www.oracle.com/kr/java/technologies/javase/jdk11-archive-downloads.html)
- sample.apk 악성 애플리케이션 다운

**2. dex파일 복호화 및 리패키징**

-복호화

![Decrypt.png](https://github.com/kdjehdwls/MobileSandbox_MobSF/blob/master/img/Decrypt.png)

-리패키징

![de_repack.png](https://github.com/kdjehdwls/MobileSandbox_MobSF/blob/master/img/de_repack.png)



**3. 리패키징한 apk파일 서명 후 에뮬레이터 설치**

- apk파일 서명
- 
![sign.jpg](https://github.com/kdjehdwls/MobileSandbox_MobSF/blob/master/img/sign.jpg)

- apk 설치
- 
![install.png](https://github.com/kdjehdwls/MobileSandbox_MobSF/blob/master/img/install.png)

**4. jadx분석 및 Frida 우회Script 만들기**


**5. Frida코드 주입을 통한 우회하기 및 어플 실행**

![frida.png](https://github.com/kdjehdwls/MobileSandbox_MobSF/blob/master/img/frida.png)

**6. MobSF API를 이용한 분석 자동화**



**[🔗시연영상 링크](https://youtu.be/rsbWD3IgQtY)**
