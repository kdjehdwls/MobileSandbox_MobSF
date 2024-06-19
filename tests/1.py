import subprocess
# Python의 'subprocess' 라이브러리를 임포트합니다. 이 라이브러리는 Python 코드 내에서
# 새로운 프로세스를 시작할 수 있게 해주며, 해당 프로세스와의 통신을 위한 파이프 접근과,
# 프로세스의 반환값을 얻을 수 있는 기능을 제공합니다. 여기서는 apktool을 사용하여 APK 파일을
# 디컴파일하고 재컴파일하는 외부 명령을 실행하는 데 사용됩니다.

import os
# Python의 'os' 모듈을 임포트합니다. 이 모듈은 운영체제와 관련된 다양한 기능을 제공합니다.
# 파일과 디렉토리를 다루는 작업, 시스템의 환경 변수에 접근하는 작업, 운영체제에 관한 정보를
# 얻는 작업 등을 수행할 때 사용됩니다. 이 스크립트에서는 파일 시스템을 탐색하고, 디렉토리를
# 생성하는 등의 작업에 사용됩니다.

import requests
# Python의 'requests' 라이브러리를 임포트합니다. 'requests'는 HTTP 요청을 쉽게 할 수 있게 해주는
# 외부 라이브러리입니다. RESTful API와의 통신, 웹 페이지의 내용을 가져오는 등 HTTP를 통한
# 데이터 교환 작업을 할 때 사용됩니다. 이 스크립트에서는 MobSF API와의 통신에 사용됩니다.

from Cryptodome.Cipher import AES
# 'Cryptodome.Cipher' 패키지에서 'AES' 모듈을 임포트합니다. AES(Advanced Encryption Standard)는
# 널리 사용되는 대칭 키 암호화 알고리즘입니다. 이 모듈을 사용하여 데이터를 암호화하거나 복호화할 수 있습니다.
# 이 스크립트에서는 'kill'로 시작하는 DEX 파일을 복호화하는 데 사용됩니다.

import glob
# Python의 'glob' 모듈을 임포트합니다. 'glob' 모듈은 파일 시스템 내에서 패턴 매칭을 사용해
# 파일 목록을 찾는 함수를 제공합니다. 주로 와일드카드 패턴을 사용하여 특정 패턴이나 확장자를
# 가진 파일을 찾을 때 사용됩니다. 이 스크립트에서는 특정 패턴('kill*.dex')을 가진 파일을 찾는 데 사용됩니다.

def decompile_apk(apk_path, output_dir):
    # 'decompile_apk' 함수는 주어진 APK 파일의 경로와 출력 디렉토리를 매개변수로 받아서 해당 APK 파일을 디컴파일합니다.
    try:
        # 'subprocess.run'을 사용하여 'apktool' 명령어를 실행합니다. 이 명령은 APK 파일을 디컴파일하고 결과를 출력 디렉토리에 저장합니다.
        # '-r' 옵션은 리소스 디코딩을 생략하고, '-s' 옵션은 소스 디코딩을 생략하며, '-f' 옵션은 이전 디컴파일 결과를 덮어쓰도록 합니다.
        subprocess.run(['C:\\Windows\\apktool.bat', 'd', apk_path, '-o', output_dir, '-r', '-s', '-f'], input=b'\n', check=True)
        print(f"APK 디컴파일 성공: {apk_path}")  # 디컴파일 성공 메시지를 출력합니다.
        return True  # 디컴파일 성공 시 True를 반환합니다.
    except subprocess.CalledProcessError as e:
        print(f"APK 디컴파일 실패: {e}")  # 디컴파일 실패 시 예외 정보와 함께 실패 메시지를 출력합니다.
        return False  # 디컴파일 실패 시 False를 반환합니다.

def find_nested_apks_and_decompile(decompiled_dir):
    # 'find_nested_apks_and_decompile' 함수는 주어진 디컴파일된 디렉토리에서 중첩된 APK 파일들을 찾아 디컴파일하는 역할을 합니다.
    for root, dirs, files in os.walk(decompiled_dir):  # 'os.walk'를 사용하여 디컴파일된 디렉토리를 순회합니다.
        for file in files:  # 디렉토리 내의 각 파일에 대해 반복합니다.
            if file.endswith('.apk'):  # 파일 이름이 '.apk'로 끝나는 경우 (APK 파일인 경우)
                nested_apk_path = os.path.join(root, file)  # 중첩된 APK 파일의 전체 경로를 구성합니다.
                nested_decompiled_dir = nested_apk_path + '_decompiled'  # 중첩된 APK 파일을 디컴파일할 디렉토리 경로를 구성합니다.
                if decompile_apk(nested_apk_path, nested_decompiled_dir):  # 중첩된 APK 파일을 디컴파일하고, 성공 여부를 확인합니다.
                    process_dex_files(nested_decompiled_dir)  # 디컴파일에 성공한 경우, 해당 디렉토리 내의 DEX 파일들을 처리합니다.

def process_dex_files(decompiled_dir):
    # 'process_dex_files' 함수는 디컴파일된 디렉토리 내의 모든 DEX 파일을 찾아 처리합니다.
    dex_files = glob.glob(os.path.join(decompiled_dir, '**', 'kill*.dex'), recursive=True)  # 'glob'를 사용하여 'kill'로 시작하는 모든 DEX 파일의 경로를 찾습니다. '**'는 모든 디렉토리를 의미하며, 'recursive=True'로 설정하여 모든 하위 디렉토리가 검색됩니다.
    for dex_file in dex_files:  # 찾은 DEX 파일들을 순회합니다.
        dex_dir = os.path.dirname(dex_file)  # DEX 파일의 디렉토리 경로를 추출합니다.
        dex_base_name = os.path.basename(dex_file)  # DEX 파일의 기본 이름(경로 없이 파일 이름만)을 추출합니다.
        decrypted_dex_name = dex_base_name.replace('kill', 'decrypted_kill')  # 파일 이름에서 'kill'을 'decrypted_kill'로 변경하여 복호화된 DEX 파일의 이름을 생성합니다.
        decrypted_dex_path = os.path.join(dex_dir, decrypted_dex_name)  # 복호화된 DEX 파일의 전체 경로를 생성합니다.
        decrypt_dex(dex_file, decrypted_dex_path, aes_key)  # 'decrypt_dex' 함수를 호출하여 DEX 파일을 복호화합니다.

def decrypt_dex(encrypted_dex_path, decrypted_dex_path, aes_key):
    # 'decrypt_dex' 함수는 주어진 경로의 암호화된 DEX 파일을 복호화합니다.
    try:
        with open(encrypted_dex_path, 'rb') as encrypted_file:  # 암호화된 DEX 파일을 바이너리 읽기 모드로 엽니다.
            encrypted_data = encrypted_file.read()  # 파일의 모든 내용을 읽어서 바이트 데이터로 저장합니다.
        cipher = AES.new(aes_key, AES.MODE_ECB)  # AES 암호화 객체를 생성합니다. 여기서 ECB 모드를 사용합니다.
        decrypted_data = cipher.decrypt(encrypted_data)  # 암호화된 데이터를 복호화합니다.
        with open(decrypted_dex_path, 'wb') as decrypted_file:  # 복호화된 데이터를 저장할 파일을 바이너리 쓰기 모드로 엽니다.
            decrypted_file.write(decrypted_data)  # 복호화된 데이터를 파일에 씁니다.
        print(f"DEX 복호화 성공: {encrypted_dex_path} -> {decrypted_dex_path}")  # 복호화 성공 메시지를 출력합니다.
        os.remove(encrypted_dex_path)  # 원본 암호화된 DEX 파일을 삭제합니다.
    except Exception as e:
        print(f"DEX 복호화 실패: {e}")  # 복호화 과정에서 예외가 발생한 경우 실패 메시지를 출력합니다.

def recompile_apk(decompiled_dir, output_apk_path, keystore_path, keystore_password, key_alias):
    # 'recompile_apk' 함수는 디컴파일된 디렉토리를 재컴파일하고, 생성된 APK 파일에 서명하는 역할을 합니다.
    try:
        # 'subprocess.run'을 사용하여 'apktool'을 이용해 디컴파일된 디렉토리를 재컴파일합니다. 결과 APK 파일은 'output_apk_path'에 저장됩니다.
        subprocess.run(['C:\\Windows\\apktool.bat', 'b', decompiled_dir, '-o', output_apk_path, '-f'], input=b'\n', check=True)
        print(f"APK 재컴파일 성공: {output_apk_path}")  # 재컴파일 성공 메시지를 출력합니다.
        
        # 'jarsigner'를 사용하여 APK 파일에 서명합니다. 서명에는 keystore 파일, keystore 비밀번호, 그리고 키 별칭이 사용됩니다.
        sign_cmd = [
            'jarsigner', 
            '-verbose',  # 상세한 출력을 활성화합니다.
            '-sigalg', 'SHA1withRSA',  # 서명 알고리즘으로 'SHA1withRSA'를 사용합니다.
            '-digestalg', 'SHA1',  # 다이제스트 알고리즘으로 'SHA1'을 사용합니다.
            '-keystore', keystore_path,  # keystore 파일의 경로를 지정합니다.
            output_apk_path,  # 서명할 APK 파일의 경로를 지정합니다.
            key_alias,  # 사용할 키의 별칭을 지정합니다.
            '-storepass', keystore_password  # keystore의 비밀번호를 지정합니다.
        ]
        subprocess.run(sign_cmd, check=True)  # 서명 명령을 실행합니다.
        print(f"APK 서명 성공: {output_apk_path}")  # 서명 성공 메시지를 출력합니다.
    except subprocess.CalledProcessError as e:
        print(f"APK 재컴파일 또는 서명 실패: {e}")  # 재컴파일 또는 서명 과정에서 오류가 발생한 경우, 실패 메시지를 출력합니다.

class MobSF_API:
    # 'MobSF_API' 클래스는 Mobile Security Framework(MobSF)의 REST API와의 통신을 관리합니다.
    def __init__(self, server, api_key, file_path):
        # 생성자 메소드는 MobSF 서버의 URL, API 키, 그리고 분석할 파일의 경로를 초기화합니다.
        self.server = server  # MobSF 서버의 URL
        self.api_key = api_key  # API 키
        self.file_path = file_path  # 분석할 파일의 경로

    def upload(self):
        # 'upload' 메소드는 파일을 MobSF 서버에 업로드하고, 업로드 성공 시 해당 파일의 해시를 반환합니다.
        print("파일을 MobSF 서버에 업로드 중...")  # 업로드 시작 메시지를 출력합니다.
        with open(self.file_path, 'rb') as f:  # 분석할 파일을 바이너리 읽기 모드로 엽니다.
            files = {'file': (os.path.basename(self.file_path), f, 'application/octet-stream')}  # 업로드할 파일 정보를 설정합니다.
            headers = {'Authorization': self.api_key}  # API 키를 사용하여 인증 헤더를 설정합니다.
            response = requests.post(f'{self.server}/api/v1/upload', files=files, headers=headers)  # 파일을 업로드하는 POST 요청을 보냅니다.
            result = response.json()  # 응답으로부터 JSON 결과를 파싱합니다.
            if response.status_code == 200 and 'hash' in result:  # 응답 상태 코드가 200이고, 결과에 'hash' 키가 있는 경우
                print("업로드 성공.")  # 업로드 성공 메시지를 출력합니다.
                return result['hash']  # 파일의 해시 값을 반환합니다.
            else:
                print("업로드 실패.")  # 업로드 실패 메시지를 출력합니다.
                return None  # 실패한 경우 None을 반환합니다.

    def scan(self, file_hash):
        # 'scan' 메소드는 업로드된 파일에 대한 스캔을 시작합니다. 파일의 해시 값을 매개변수로 받습니다.
        print("업로드된 파일 스캔 시작...")  # 스캔 시작 메시지를 출력합니다.
        data = {'hash': file_hash}  # 스캔할 파일의 해시 값을 데이터로 설정합니다.
        headers = {'Authorization': self.api_key}  # API 키를 사용하여 인증 헤더를 설정합니다.
        response = requests.post(f'{self.server}/api/v1/scan', data=data, headers=headers)  # 스캔을 시작하는 POST 요청을 보냅니다.
        result = response.json()  # 응답으로부터 JSON 결과를 파싱합니다.
        if response.status_code == 200:  # 응답 상태 코드가 200인 경우
            print("스캔 성공적으로 시작됨.")  # 스캔 시작 성공 메시지를 출력합니다.
            return result  # 스캔 결과를 반환합니다.
        else:
            print("스캔 시작 실패.")  # 스캔 시작 실패 메시지를 출력합니다.
            return None  # 실패한 경우 None을 반환합니다.

    def download_pdf_report(self, file_hash):
        # 'download_pdf_report' 메소드는 스캔된 파일의 PDF 보고서를 다운로드합니다. 파일의 해시 값을 매개변수로 받습니다.
        print("스캔된 파일의 PDF 보고서 다운로드 중...")  # PDF 보고서 다운로드 시작 메시지를 출력합니다.
        data = {'hash': file_hash}  # 다운로드할 보고서의 파일 해시 값을 데이터로 설정합니다.
        headers = {'Authorization': self.api_key}  # API 키를 사용하여 인증 헤더를 설정합니다.
        response = requests.post(f'{self.server}/api/v1/download_pdf', data=data, headers=headers, stream=True)  # PDF 보고서를 다운로드하는 POST 요청을 보냅니다.
        if response.status_code == 200:  # 응답 상태 코드가 200인 경우
            pdf_path = f'{os.path.splitext(self.file_path)[0]}_report.pdf'  # 저장할 PDF 파일의 경로를 설정합니다.
            with open(pdf_path, 'wb') as f:  # PDF 파일을 바이너리 쓰기 모드로 엽니다.
                for chunk in response.iter_content(chunk_size=1024):  # 응답으로부터 데이터를 1024 바이트 단위로 받아옵니다.
                    if chunk:  # 받아온 데이터 청크가 있는 경우
                        f.write(chunk)  # 데이터 청크를 파일에 씁니다.
            print(f"PDF 보고서가 {pdf_path}에 성공적으로 다운로드됨.")  # PDF 보고서 다운로드 성공 메시지를 출력합니다.
        else:
            print("PDF 보고서 다운로드 실패.")  # PDF 보고서 다운로드 실패 메시지를 출력합니다.

    def start_dynamic_analysis(self, file_hash):
        # 'start_dynamic_analysis' 메소드는 업로드된 파일에 대한 동적 분석을 시작합니다. 파일의 해시 값을 매개변수로 받습니다.
        print("동적 분석 시작 중...")  # 동적 분석 시작 메시지를 출력합니다.
        data = {'hash': file_hash}  # 분석할 파일의 해시 값을 데이터로 설정합니다.
        headers = {'Authorization': self.api_key}  # API 키를 사용하여 인증 헤더를 설정합니다.
        response = requests.post(f'{self.server}/api/v1/dynamic/start_analysis', data=data, headers=headers)  # 동적 분석을 시작하는 POST 요청을 보냅니다.
        result = response.json()  # 응답으로부터 JSON 결과를 파싱합니다.
        if response.status_code == 200:  # 응답 상태 코드가 200인 경우
            print("동적 분석이 성공적으로 시작됨.")  # 동적 분석 시작 성공 메시지를 출력합니다.
            return result  # 동적 분석 결과를 반환합니다.
        else:
            print("동적 분석 시작 실패.")  # 동적 분석 시작 실패 메시지를 출력합니다.
            return None  # 실패한 경우 None을 반환합니다.

    def get_dynamic_analysis_status(self, file_hash):
        # 'get_dynamic_analysis_status' 메소드는 동적 분석의 상태를 확인합니다. 파일의 해시 값을 매개변수로 받습니다.
        print("동적 분석 상태 확인 중...")  # 동적 분석 상태 확인 메시지를 출력합니다.
        headers = {'Authorization': self.api_key}  # API 키를 사용하여 인증 헤더를 설정합니다.
        response = requests.get(f'{self.server}/api/v1/dynamic/status', headers=headers, params={'hash': file_hash})  # 동적 분석 상태를 확인하는 GET 요청을 보냅니다.
        result = response.json()  # 응답으로부터 JSON 결과를 파싱합니다.
        if response.status_code == 200:  # 응답 상태 코드가 200인 경우
            print("동적 분석 상태: ", result['status'])  # 동적 분석의 현재 상태를 출력합니다.
            return result  # 동적 분석 상태 정보를 반환합니다.
        else:
            print("동적 분석 상태 확인 실패.")  # 동적 분석 상태 확인 실패 메시지를 출력합니다.
            return None  # 실패한 경우 None을 반환합니다.

    def stop_dynamic_analysis(self, file_hash):
        # 'stop_dynamic_analysis' 메소드는 동적 분석을 멈추고 필요한 정리 작업을 수행합니다. 파일의 해시 값을 매개변수로 받습니다.
        print("동적 분석을 멈추는 중...")  # 동적 분석 중지 메시지를 출력합니다.
        data = {'hash': file_hash}  # 분석을 멈출 파일의 해시 값을 데이터로 설정합니다.
        headers = {'Authorization': self.api_key}  # API 키를 사용하여 인증 헤더를 설정합니다.
        response = requests.post(f'{self.server}/api/v1/dynamic/stop_analysis', data=data, headers=headers)  # 동적 분석을 멈추는 POST 요청을 보냅니다.
        if response.status_code == 200:  # 응답 상태 코드가 200인 경우
            print("동적 분석이 성공적으로 멈춰짐.")  # 동적 분석 중지 성공 메시지를 출력합니다.
        else:
            print(f"동적 분석을 멈추는 데 실패했습니다. 응답 코드: {response.status_code}")  # 동적 분석 중지 실패 메시지를 출력합니다.

    def download_dynamic_report(self, file_hash):
        # 'download_dynamic_report' 메소드는 동적 분석 리포트를 다운로드합니다. 파일의 해시 값을 매개변수로 받습니다.
        print("동적 분석 리포트 다운로드 중...")  # 동적 분석 리포트 다운로드 시작 메시지를 출력합니다.
        headers = {'Authorization': self.api_key}  # API 키를 사용하여 인증 헤더를 설정합니다.
        data = {'hash': file_hash}  # 다운로드할 리포트의 파일 해시 값을 데이터로 설정합니다.
        response = requests.post(f'{self.server}/api/v1/dynamic/report_json', headers=headers, data=data)  # 동적 분석 리포트를 다운로드하는 POST 요청을 보냅니다.
        if response.status_code == 200:  # 응답 상태 코드가 200인 경우
            report_path = f'{os.path.splitext(self.file_path)[0]}_dynamic_report.json'  # 저장할 동적 분석 리포트 파일의 경로를 설정합니다.
            with open(report_path, 'wb') as f:  # 동적 분석 리포트 파일을 바이너리 쓰기 모드로 엽니다.
                f.write(response.content)  # 응답의 내용(동적 분석 리포트)을 파일에 씁니다.
            print(f"동적 분석 리포트가 {report_path}에 성공적으로 다운로드됨.")  # 동적 분석 리포트 다운로드 성공 메시지를 출력합니다.
        else:
            print("동적 분석 리포트 다운로드 실패.")  # 동적 분석 리포트 다운로드 실패 메시지를 출력합니다.

if __name__ == "__main__":
    # 이 조건문은 이 스크립트가 직접 실행될 때만 아래의 코드가 실행되도록 합니다. 모듈로 임포트될 때는 실행되지 않습니다.

    server_url = 'http://127.0.0.1:8000'
    # MobSF 서버의 URL을 변수에 할당합니다. MobSF가 실행되고 있는 로컬 또는 원격 서버의 주소입니다.

    api_key = '816b6bbd700d4dd27eb9ed1da4017e3023284a1ebd56683f9eeb21962463fa62'
    # MobSF의 REST API를 사용하기 위한 API 키를 변수에 할당합니다. 이 키는 MobSF 서버에서 생성되고 관리됩니다.

    apk_path = 'C:\\Users\\HP\\Desktop\\sandbox\\sample.apk'
    # 분석할 APK 파일의 경로를 변수에 할당합니다. 이 경로는 실제 APK 파일의 위치를 반영해야 합니다.

    aes_key = b'dbcdcfghijklmaop'
    # DEX 파일을 복호화할 때 사용할 AES 키를 바이트 문자열로 변수에 할당합니다.

    decompiled_dir = 'C:\\Users\\HP\\Desktop\\sandbox\\decompiled_apk'
    # APK 파일을 디컴파일한 결과를 저장할 디렉토리의 경로를 변수에 할당합니다.

    output_dir = 'C:\\Users\\HP\\Desktop\\sandbox'
    # 재컴파일된 APK 파일 및 기타 출력 파일을 저장할 디렉토리의 경로를 변수에 할당합니다.

    keystore_path = 'C:\\Users\\HP\\Desktop\\sandbox\\cloudwoon.keystore'
    # APK 파일을 재컴파일한 후 서명하는 데 사용할 keystore 파일의 경로를 변수에 할당합니다.

    keystore_password = 'cloudwoon'
    # keystore에 접근하기 위한 비밀번호를 변수에 할당합니다.

    key_alias = 'cloudwoon'
    # keystore 내에서 사용할 특정 키의 별칭을 변수에 할당합니다.

    bypass_script_path = 'C:\\Users\\HP\\Desktop\\sandbox\\bypass_script.js'
    # 안티 VM(가상 머신) 기능을 우회하기 위해 사용할 Frida 스크립트의 경로를 변수에 할당합니다.

    package_name = 'com.ldjSxw.heBbQd'
    # 동적 분석을 수행할 때 타겟이 되는 APK 파일의 패키지 이름을 변수에 할당합니다.

    # 아래의 함수들은 위에서 정의한 변수들을 사용하여 APK 파일의 디컴파일, 재컴파일, 서명, 분석 등의 작업을 수행합니다.
    decompile_apk(apk_path, decompiled_dir)
    # 'decompile_apk' 함수를 호출하여 APK 파일을 디컴파일합니다. 'apk_path'와 'decompiled_dir'을 인자로 넘깁니다.

    find_nested_apks_and_decompile(decompiled_dir)
    # 'find_nested_apks_and_decompile' 함수를 호출하여 디컴파일된 디렉토리 내에서 중첩된 APK 파일을 찾아 디컴파일합니다.

    process_dex_files(decompiled_dir)
    # 'process_dex_files' 함수를 호출하여 디컴파일된 디렉토리 내의 DEX 파일들을 처리합니다.

    recompiled_apk_path = os.path.join(output_dir, 're_sample.apk')
    # 재컴파일된 APK 파일을 저장할 경로를 'output_dir'과 파일 이름을 결합하여 생성합니다.

    recompile_apk(decompiled_dir, recompiled_apk_path, keystore_path, keystore_password, key_alias)
    # 'recompile_apk' 함수를 호출하여 디컴파일된 디렉토리를 재컴파일하고, 결과 APK 파일에 서명합니다.

    mobSF = MobSF_API(server_url, api_key, recompiled_apk_path)
    # 'MobSF_API' 클래스의 인스턴스를 생성합니다. MobSF 서버의 URL, API 키, 재컴파일된 APK 파일의 경로를 인자로 넘깁니다.

    file_hash = mobSF.upload()
    # 'upload' 메소드를 호출하여 재컴파일된 APK 파일을 MobSF 서버에 업로드하고, 파일의 해시 값을 반환받습니다.

    if file_hash:
        # 파일 해시 값이 성공적으로 반환되었다면, 아래의 코드 블록이 실행됩니다.
        mobSF.scan(file_hash)
        # 'scan' 메소드를 호출하여 업로드된 파일에 대한 정적 분석을 시작합니다.

        mobSF.download_pdf_report(file_hash)
        # 'download_pdf_report' 메소드를 호출하여 정적 분석의 결과인 PDF 보고서를 다운로드합니다.

        dynamic_results = mobSF.start_dynamic_analysis(file_hash)
        # 'start_dynamic_analysis' 메소드를 호출하여 업로드된 파일에 대한 동적 분석을 시작합니다.

        if dynamic_results:
            # 동적 분석이 성공적으로 시작되었다면, 아래의 코드 블록이 실행됩니다.
            mobSF.bypass_anti_vm(package_name, bypass_script_path)
            # 'bypass_anti_vm' 메소드를 호출하여 안티 VM 기능을 우회합니다.

            mobSF.stop_dynamic_analysis(file_hash)
            # 'stop_dynamic_analysis' 메소드를 호출하여 동적 분석을 중지합니다.

            mobSF.download_dynamic_report(file_hash)
            # 'download_dynamic_report' 메소드를 호출하여 동적 분석의 결과인 리포트를 다운로드합니다.
