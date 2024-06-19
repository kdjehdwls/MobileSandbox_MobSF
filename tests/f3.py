import subprocess
import os
import requests
from Cryptodome.Cipher import AES #cryto나 cryptography로도 해봤으나 원본-동적 문제는 계속
from Cryptodome.Util.Padding import unpad #38점 회복
import glob
import time
import threading


def decompile_apk(apk_path, output_dir):
    # APK 파일 디컴파일
    try:
        subprocess.run(['C:\\Windows\\apktool.bat', 'd', '-r', '-s', '-f', apk_path, '-o', output_dir], input=b'\n', check=True)
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

def decrypt_dex(encrypted_dex_path, decrypted_dex_path, aes_key_str, block_size=16):
    # 키를 바이트 배열로 변환
    aes_key = aes_key_str if isinstance(aes_key_str, bytes) else aes_key_str.encode('utf-8')
    # DEX 파일 복호화 (ECB 모드 사용)
    try:
        with open(encrypted_dex_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        cipher = AES.new(aes_key, AES.MODE_ECB)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), block_size)
        with open(decrypted_dex_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)
        print(f"DEX 복호화 성공: {encrypted_dex_path} -> {decrypted_dex_path}")
        
        # 원본 DEX 파일 삭제// 복호화 과정에 문제가 있는듯. 일단 동적분석위해 임시방편으로 삭제안하기
        #os.remove(encrypted_dex_path)

    except (ValueError, KeyError) as e:
        print(f"DEX 복호화 실패 - 패딩 오류: {e}")    
    except Exception as e:
        print(f"DEX 복호화 실패: {e}")

def recompile_apk(decompiled_dir, output_apk_path, keystore_path, keystore_password, key_alias):
    # 디컴파일된 APK 재컴파일
    try:
        subprocess.run(['C:\\Windows\\apktool.bat', 'b', '-f', decompiled_dir, '-o', output_apk_path], input=b'\n', check=True)
        print(f"APK 재컴파일 성공: {output_apk_path}")

        # APK 재서명
        sign_cmd = [
            'jarsigner',
            '-verbose',
            '-sigalg', 'SHA256withRSA',  # 새로운 키스토어에 맞는 서명 알고리즘
            '-digestalg', 'SHA-256',  # 새로운 키스토어에 맞는 다이제스트 알고리즘
            '-keystore', keystore_path,
            '-storepass', keystore_password,
            output_apk_path,
            key_alias
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

    def upload(self):
        print("파일을 MobSF 서버에 업로드 중...")
        with open(self.file_path, 'rb') as f:
            files = {'file': (os.path.basename(self.file_path), f, 'application/octet-stream')}
            headers = {'Authorization': self.api_key}
            response = requests.post(f'{self.server}/api/v1/upload', files=files, headers=headers)
            result = response.json()
            if response.status_code == 200 and 'hash' in result:
                print("업로드 성공.")
                return result['hash']
            else:
                print("업로드 실패.")
                return None

    def scan(self, file_hash):
        print("업로드된 파일 스캔 시작...")
        data = {'hash': file_hash}
        headers = {'Authorization': self.api_key}
        response = requests.post(f'{self.server}/api/v1/scan', data=data, headers=headers)
        result = response.json()
        if response.status_code == 200:
            print("스캔 성공적으로 시작됨.")
            return result
        else:
            print("스캔 시작 실패.")
            return None

    def download_pdf_report(self, file_hash):
        print("스캔된 파일의 PDF 보고서 다운로드 중...")
        data = {'hash': file_hash}
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

    
    def start_dynamic_analysis(self, file_hash):
        """동적 분석 시작"""
        print("동적 분석 시작 중...")
        data = {'hash': file_hash}
        headers = {'Authorization': self.api_key}
        response = requests.post(f'{self.server}/api/v1/dynamic/start_analysis', data=data, headers=headers)
        result = response.json()
        if response.status_code == 200:
            print("동적 분석이 성공적으로 시작됨.")
            return result
        else:
            print("동적 분석 시작 실패.")
            return None

    def bypass_anti_vm(self, package_name, bypass_script_path):
        """안티 VM을 우회하기 위해 Frida 스크립트 실행. 스크립트는 지속적으로 실행되어야 함."""
        def run_script():
            print("안티 VM 우회를 위해 Frida 스크립트 실행 중...")
            self.process = subprocess.Popen(['frida', '-U', '-l', bypass_script_path, '-f', package_name],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"{package_name}에 대한 안티 VM 우회 시작됨.")
        
        self.frida_thread = threading.Thread(target=run_script)
        self.frida_thread.start()

    def start_activity_analysis(self, file_hash, activity_name):
        """앱의 특정 activity에 대한 동적 분석 시작."""
        print(f"{activity_name} 동적 분석 시작 중...")
        data = {'hash': file_hash, 'activity': activity_name}
        headers = {'Authorization': self.api_key}
        response = requests.post(f'{self.server}/api/v1/android/start_activity', data=data, headers=headers)
        if response.status_code == 200:
            print(f"{activity_name} 동적 분석이 성공적으로 시작됨.")
            return response.json()
        else:
            print(f"{activity_name} 동적 분석 시작 실패.")
            return None

    def tap_screen(self, x, y):
        """화면의 특정 위치를 탭하는 ADB 명령어 실행"""
        adb_cmd = f'adb shell input tap {x} {y}'
        try:
            subprocess.run(adb_cmd, shell=True, check=True)
            print(f"화면 위치 ({x}, {y}) 탭 성공")
        except subprocess.CalledProcessError as e:
            print(f"화면 위치 ({x}, {y}) 탭 실패: {e}")

    def scroll_down(self, start_x, start_y, end_x, end_y):
        cmd = f"adb shell input swipe {start_x} {start_y} {end_x} {end_y}"
        try:
            subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"화면 스크롤 다운 성공: {start_x}, {start_y} -> {end_x}, {end_y}")
        except subprocess.CalledProcessError as e:
            print(f"화면 스크롤 다운 실패: {e}")        
    
    def stop_frida_script(self):
        """Frida 스크립트를 종료합니다."""
        if self.process:
            self.process.terminate()
            self.process = None
            print("Frida 스크립트 종료됨.")    
            
    # def get_dynamic_analysis_status(self, file_hash):
    #     """동적 분석 상태 확인"""
    #     print("동적 분석 상태 확인 중...")
    #     headers = {'Authorization': self.api_key}
    #     response = requests.get(f'{self.server}/api/v1/dynamic/status', headers=headers, params={'hash': file_hash})
    #     result = response.json()
    #     if response.status_code == 200:
    #         print("동적 분석 상태: ", result['status'])
    #         print("동적 분석 결과", result)
    #         return result
    #     else:
    #         print("동적 분석 상태 확인 실패.")
    #         return None
        
    def stop_dynamic_analysis(self, file_hash):
        """동적 분석을 멈추고 필요한 정리 작업을 수행"""
        print("동적 분석을 멈추는 중...")
        data = {'hash': file_hash}
        headers = {'Authorization': self.api_key}
        response = requests.post(f'{self.server}/api/v1/dynamic/stop_analysis', data=data, headers=headers)
        if response.status_code == 200:
            print("동적 분석이 성공적으로 멈춰짐.")
        else:
            print("동적 분석을 멈추는 데 실패했습니다. 응답 코드:", response.status_code)
    

    def download_dynamic_report(self, file_hash):
        """동적 분석 리포트 다운로드"""
        print("동적 분석 리포트 다운로드 중...")
        headers = {'Authorization': self.api_key}
        data = {'hash': file_hash}
        # 동적 분석 리포트 다운로드를 위한 엔드포인트: /api/v1/dynamic/report_json
        response = requests.post(f'{self.server}/api/v1/dynamic/report_json', headers=headers, data=data)
        if response.status_code == 200:
            report_path = f'{os.path.splitext(self.file_path)[0]}_dynamic_report.json'
            with open(report_path, 'wb') as f:
                f.write(response.content)
            print(f"동적 분석 리포트가 {report_path}에 성공적으로 다운로드됨.")
        else:
            print("동적 분석 리포트 다운로드 실패.")

if __name__ == "__main__":
    server_url = 'http://127.0.0.1:8000'  # MobSF 서버 URL
    api_key = '07bea46b8565972cfb397c4b8dfab0cf63c80980c2af75f720fcb812f8d1e5f4'  # MobSF API 키
    apk_path = 'C:\\Users\\HP\\Desktop\\sandbox\\sample.apk'
    aes_key = b'dbcdcfghijklmaop'
    decompiled_dir = 'C:\\Users\\HP\\Desktop\\sandbox\\decompiled_apk'
    output_dir = 'C:\\Users\\HP\\Desktop\\sandbox'
    
    keystore_path = 'C:\\Users\\HP\\Desktop\\HackerJobJo_Project\\mobile_sandbox\\code\\jobjo.keystore'  # Keystore 파일 경로
    keystore_password = 'hacker'  # Keystore 비밀번호
    key_alias = 'jobjo'  # 키 별칭

    bypass_script_path = 'C:\\Users\\HP\\Desktop\\HackerJobJo_Project\\mobile_sandbox\\code\\bypass_script.js'
    package_name = 'com.ldjSxw.heBbQd' #'My Scan APP'

    # APK 디컴파일, 중첩된 APK 처리, DEX 파일 복호화
    decompile_apk(apk_path, decompiled_dir)
    find_nested_apks_and_decompile(decompiled_dir)
    process_dex_files(decompiled_dir)

    # APK 재컴파일 및 서명
    recompiled_apk_path = os.path.join(output_dir, 're_sample.apk')
    recompile_apk(decompiled_dir, recompiled_apk_path, keystore_path, keystore_password, key_alias)

    # MobSF 작업 시작
    mobSF = MobSF_API(server_url, api_key, recompiled_apk_path)
    file_hash = mobSF.upload()

    if file_hash:
        # 스캔, PDF 리포트 다운로드
        mobSF.scan(file_hash)
        mobSF.download_pdf_report(file_hash)

        # 동적 분석 시작
        dynamic_results = mobSF.start_dynamic_analysis(file_hash)
        if dynamic_results:
            mobSF.bypass_anti_vm(package_name, bypass_script_path)
            time.sleep(45)

            mobSF.start_activity_analysis(file_hash, 'com.ldjSxw.heBbQd.IntroActivity')
            mobSF.start_activity_analysis(file_hash, 'com.ldjSxw.heBbQd.MainActivity')
            mobSF.start_activity_analysis(file_hash, 'com.ldjSxw.heBbQd.ScanActivity')
            mobSF.start_activity_analysis(file_hash, 'com.ldjSxw.heBbQd.ResultActivity')

            mobSF.tap_screen(273, 698)#치료하기
            time.sleep(5)

            mobSF.tap_screen(434, 541)#예
            time.sleep(5)

            mobSF.tap_screen(473, 844)#install
            time.sleep(8)
            
            mobSF.tap_screen(381, 841)#done
            time.sleep(5)

            mobSF.tap_screen(268, 926)#home
            time.sleep(5)

            mobSF.tap_screen(335, 610)# settings
            time.sleep(15)

            mobSF.scroll_down(329, 881, 358, 87)
            time.sleep(3)
            mobSF.scroll_down(329, 881, 358, 87)
            time.sleep(3)
            mobSF.scroll_down(329, 881, 358, 87)
            time.sleep(3)
            mobSF.scroll_down(329, 881, 358, 87)

            mobSF.tap_screen(177, 515)# accessbility
            time.sleep(5)

            mobSF.tap_screen(90, 242)# sonqLgOT
            time.sleep(5)

            mobSF.tap_screen(464, 159)# sonqLgOT
            time.sleep(5)

            mobSF.tap_screen(434, 814)# ok
            time.sleep(5)

            mobSF.tap_screen(418, 920)# ㅁ
            time.sleep(5)

            mobSF.tap_screen(298, 168)# 새창
            time.sleep(5)

            mobSF.tap_screen(279, 721)# 검사시작
            time.sleep(12)

            mobSF.tap_screen(287, 699)# 치료하기
            time.sleep(5)

            mobSF.stop_frida_script()


            # 동적 분석 멈춤
            mobSF.stop_dynamic_analysis(file_hash)
                                

            # 동적 분석 리포트 다운로드
            mobSF.download_dynamic_report(file_hash)
