import subprocess
import os
import requests
from Cryptodome.Cipher import AES
import glob

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
        decrypt_dex(dex_file, decrypted_dex_path, aes_key)  # aes_iv 인자 제거

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

def main():
    server_url = 'http://127.0.0.1:8000'  # MobSF 서버 URL
    api_key = '816b6bbd700d4dd27eb9ed1da4017e3023284a1ebd56683f9eeb21962463fa62'  # MobSF API 키
    apk_path = 'C:\\Users\\HP\\Desktop\\sandbox\\sample.apk'
    decompiled_dir = 'C:\\Users\\HP\\Desktop\\sandbox\\decompiled_apk'
    output_dir = 'C:\\Users\\HP\\Desktop\\sandbox'

    keystore_path = 'C:\\Users\\HP\\Desktop\\sandbox\\cloudwoon.keystore'  # Keystore 파일 경로
    keystore_password = 'cloudwoon'  # Keystore 비밀번호
    key_alias = 'cloudwoon'  # 키 별칭

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
        scan_results = mobSF.scan(file_hash)
        if scan_results:
            mobSF.download_pdf_report(file_hash)

if __name__ == "__main__":
    aes_key = b'dbcdcfghijklmaop'
    main()
