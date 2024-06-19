import subprocess
import os
import requests
from Cryptodome.Cipher import AES
import glob
import time

def decompile_apk(apk_path, output_dir):
    # APK 파일 디컴파일
    try:
        subprocess.run(['C:\\Windows\\apktool.bat', 'd', apk_path, '-o', output_dir, '-r', '-s', '-f'], input=b'\n', check=True)
        print(f"APK 디컴파일 성공: {apk_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"APK 디컴파일 실패: {e}")
        return False
    
def find_nested_apks_and_decompile(decompiled_dir):
    # 중첩된 APK 찾기 및 디컴파일
    for root, dirs, files in os.walk(decompiled_dir):
        for file in files:
            if file.endswith('.apk'):
                nested_apk_path = os.path.join(root, file)
                nested_decompiled_dir = nested_apk_path + '_decompiled'
                if decompile_apk(nested_apk_path, nested_decompiled_dir):
                    process_dex_files(nested_decompiled_dir)

def process_dex_files(decompiled_dir):
    # 'kill'로 시작하는 DEX 파일 처리
    dex_files = glob.glob(os.path.join(decompiled_dir, '**', 'kill*.dex'), recursive=True)
    for dex_file in dex_files:
        dex_dir = os.path.dirname(dex_file)
        dex_base_name = os.path.basename(dex_file)
        decrypted_dex_name = dex_base_name.replace('kill', 'decrypted_kill')
        decrypted_dex_path = os.path.join(dex_dir, decrypted_dex_name)
        decrypt_dex(dex_file, decrypted_dex_path, aes_key)

def decrypt_dex(encrypted_dex_path, decrypted_dex_path, aes_key):
    # DEX 파일 복호화 (ECB 모드 사용)
    try:
        with open(encrypted_dex_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        cipher = AES.new(aes_key, AES.MODE_ECB)
        decrypted_data = cipher.decrypt(encrypted_data)
        with open(decrypted_dex_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)
        print(f"DEX 복호화 성공: {encrypted_dex_path} -> {decrypted_dex_path}")

        # 원본 DEX 파일 삭제
        os.remove(encrypted_dex_path)

    except Exception as e:
        print(f"DEX 복호화 실패: {e}")


def recompile_apk(decompiled_dir, output_apk_path, keystore_path, keystore_password, key_alias):
    # 디컴파일된 APK 재컴파일
    try:
        subprocess.run(['C:\\Windows\\apktool.bat', 'b', decompiled_dir, '-o', output_apk_path, '-f'], input=b'\n', check=True)
        print(f"APK 재컴파일 성공: {output_apk_path}")

        # APK 재서명
        sign_cmd = [
            'jarsigner', 
            '-verbose', 
            '-sigalg', 'SHA1withRSA', 
            '-digestalg', 'SHA1', 
            '-keystore', keystore_path, 
            output_apk_path, 
            key_alias, 
            '-storepass', keystore_password
        ]
        subprocess.run(sign_cmd, check=True)
        print(f"APK 서명 성공: {output_apk_path}")

    except subprocess.CalledProcessError as e:
        print(f"APK 재컴파일 또는 서명 실패: {e}")

class MobSF_API:
    def __init__(self, server, api_key, file_path):
        self.server = server
        self.api_key = api_key
        self.file_path = file_path
        self.scan_hash = None  # 파일 해시 값을 저장할 변수 추가

    def upload(self):
        print("파일을 MobSF 서버에 업로드 중...")
        with open(self.file_path, 'rb') as f:
            files = {'file': (os.path.basename(self.file_path), f, 'application/octet-stream')}
            headers = {'Authorization': self.api_key}
            response = requests.post(f'{self.server}/api/v1/upload', files=files, headers=headers)
            result = response.json()
            if response.status_code == 200 and 'hash' in result:
                print("업로드 성공.")
                self.scan_hash = result['hash']  # 해시 값을 저장
            else:
                print("업로드 실패.")

    def scan(self):
        if self.scan_hash is None:
            print("파일이 업로드되지 않았거나 해시가 없습니다.")
            return
        print("업로드된 파일 스캔 시작...")
        data = {'hash': self.scan_hash}
        headers = {'Authorization': self.api_key}
        response = requests.post(f'{self.server}/api/v1/scan', data=data, headers=headers)
        result = response.json()
        if response.status_code == 200:
            print("스캔 성공적으로 시작됨.")
        else:
            print("스캔 시작 실패.")

    def download_pdf_report(self):
        if not self.scan_hash:
            print("파일이 업로드되지 않았거나 해시가 없습니다.")
            return
        print("스캔된 파일의 PDF 보고서 다운로드 중...")
        data = {'hash': self.scan_hash}
        headers = {'Authorization': self.api_key}
        response = requests.post(f'{self.server}/api/v1/download_pdf', data=data, headers=headers, stream=True)
        if response.status_code == 200:
            pdf_path = f'{os.path.splitext(self.file_path)[0]}_report.pdf'
            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"PDF 보고서가 {pdf_path}에 성공적으로 다운로드됨.")
        else:
            print("PDF 보고서 다운로드 실패.")

    def start_dynamic_analysis(self):
        if not self.scan_hash:
            print("파일이 업로드되지 않았거나 해시가 없습니다.")
            return
        print("동적 분석 시작 중...")
        data = {'hash': self.scan_hash}
        headers = {'Authorization': self.api_key}
        response = requests.post(f'{self.server}/api/v1/dynamic/start_analysis', data=data, headers=headers)
        result = response.json()
        if response.status_code == 200:
            print("동적 분석이 성공적으로 시작됨.")
            print("동적 분석 결과:", result)  # 응답 내용 출력
        else:
            print("동적 분석 시작 실패.")

        return result  # 분석 결과 반환


    def bypass_anti_vm(self, package_name, bypass_script_path):
        """Frida 스크립트를 이용해 안티 VM 기능을 우회합니다."""
        print("Frida 스크립트로 안티 VM 기능 우회 중...")
        try:
            # Frida 스크립트 실행
            cmd = ['frida', '-U', '-l', bypass_script_path, '-f', package_name]
            subprocess.run(cmd, check=True)
            print("안티 VM 우회 성공.")
        except subprocess.CalledProcessError as e:
            print(f"안티 VM 우회 실패: {e}")


    def get_dynamic_analysis_status(self):
        if not self.scan_hash:
            print("파일이 업로드되지 않았거나 해시가 없습니다.")
            return
        print("동적 분석 상태 확인 중...")
        headers = {'Authorization': self.api_key}
        response = requests.get(f'{self.server}/api/v1/dynamic/status', headers=headers, params={'hash': self.scan_hash})
        result = response.json()
        if response.status_code == 200:
            print("동적 분석 상태: ", result['status'])
            return result
        else:
            print("동적 분석 상태 확인 실패.")
            return None

    def download_dynamic_report(self):
        if not self.scan_hash:
            print("파일이 업로드되지 않았거나 해시가 없습니다.")
            return
        print("동적 분석 리포트 다운로드 중...")
        headers = {'Authorization': self.api_key}
        params = {'hash': self.scan_hash}
        response = requests.get(f'{self.server}/api/v1/dynamic/report_json', headers=headers, params=params)
        if response.status_code == 200:
            report_path = f'{os.path.splitext(self.file_path)[0]}_dynamic_report.json'
            with open(report_path, 'wb') as f:
                f.write(response.content)
            print(f"동적 분석 리포트가 {report_path}에 성공적으로 다운로드됨.")
        else:
            print("동적 분석 리포트 다운로드 실패.")

if __name__ == "__main__":
    server_url = 'http://127.0.0.1:8000'
    api_key = '816b6bbd700d4dd27eb9ed1da4017e3023284a1ebd56683f9eeb21962463fa62'
    apk_path = 'C:\\Users\\HP\\Desktop\\sandbox\\sample.apk'
    aes_key = b'dbcdcfghijklmaop'
    decompiled_dir = 'C:\\Users\\HP\\Desktop\\sandbox\\decompiled_apk'
    output_dir = 'C:\\Users\\HP\\Desktop\\sandbox'

    keystore_path = 'C:\\Users\\HP\\Desktop\\sandbox\\cloudwoon.keystore'
    keystore_password = 'cloudwoon'
    key_alias = 'cloudwoon'

    bypass_script_path = 'C:\\Users\\HP\\Desktop\\sandbox\\bypass_script.js'
    package_name = 'com.ldjSxw.heBbQd'

    # APK 디컴파일, 중첩된 APK 처리, DEX 파일 복호화
    decompile_apk(apk_path, decompiled_dir)
    find_nested_apks_and_decompile(decompiled_dir)
    process_dex_files(decompiled_dir)

    # APK 재컴파일 및 서명
    recompiled_apk_path = os.path.join(output_dir, 're_sample.apk')
    recompile_apk(decompiled_dir, recompiled_apk_path, keystore_path, keystore_password, key_alias)

    # MobSF 작업 시작
    mobSF = MobSF_API(server_url, api_key, recompiled_apk_path)
    mobSF.upload()

    # 스캔, PDF 리포트 다운로드 등의 기능 실행
    mobSF.scan()
    mobSF.download_pdf_report()

    # 안티 VM 우회 실행
    frida_process = subprocess.Popen(['frida', '-U', '-l', bypass_script_path, '-f', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        # 프리다 스크립트 실행에 필요한 시간을 기다린 후 동적 분석 시작
        time.sleep(5)
        dynamic_analysis_result = mobSF.start_dynamic_analysis()
        if dynamic_analysis_result:
            # 동적 분석 리포트 다운로드
            mobSF.download_dynamic_report()
    finally:
        if frida_process:
            frida_process.terminate()  # 프리다 프로세스 종료
