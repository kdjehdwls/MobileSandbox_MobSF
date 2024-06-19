import subprocess
import os
import requests
from Cryptodome.Cipher import AES

def decompile_apk(apk_path, output_dir):
    try:
        subprocess.run(['C:\\Windows\\apktool.bat', 'd', apk_path, '-o', output_dir, '-r', '-s'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"APK 디컴파일 중 에러 발생: {e}")

def decrypt_dex(encrypted_dex_path, decrypted_dex_path, aes_key, aes_iv):
    try:
        with open(encrypted_dex_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()

        cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
        decrypted_data = cipher.decrypt(encrypted_data)

        with open(decrypted_dex_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)
    except Exception as e:
        print(f"DEX 복호화 중 에러 발생: {e}")

def recompile_apk(decompiled_dir, output_apk_path):
    try:
        subprocess.run(['C:\\Windows\\apktool.bat', 'b', decompiled_dir, '-o', output_apk_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"APK 재컴파일 중 에러 발생: {e}")

def upload_and_scan(file_path, mobsf_url, api_key):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            headers = {'X-Mobsf-Api-Key': api_key}  # 'Authorization' 대신 'X-Mobsf-Api-Key' 사용
            upload_url = os.path.join(mobsf_url, 'api/v1/upload')  # 업로드 URL 구성

            response = requests.post(upload_url, files=files, headers=headers)
            response.raise_for_status()  # 응답 상태 코드 검증

            json_response = response.json()
            if 'scan_id' not in json_response:
                raise ValueError("Scan ID를 찾을 수 없습니다.")

            # 스캔 ID를 사용하여 추가 작업 수행 가능
            scan_id = json_response['scan_id']
            return json_response
    except Exception as e:
        print(f"MobSF 업로드 및 스캔 중 에러 발생: {e}")
        return None

if __name__ == "__main__":
    apk_path = 'C:\\Users\\HP\\Desktop\\sandbox\\sample.apk'
    decompiled_dir = 'C:\\Users\\HP\\Desktop\\sandbox\\decompiled_apk'
    aes_key = b'dbcdcfghijklmaop'
    aes_iv = b'\x92\x10,\x19\xc4,@\xd1 \xa3\xbe\xa1\xc9_\xbd`'

    decompile_apk(apk_path, decompiled_dir)

    encrypted_dex_path = os.path.join(decompiled_dir, 'kill-classes.dex')
    decrypted_dex_path = os.path.join(decompiled_dir, 'classes2.dex')

    decrypt_dex(encrypted_dex_path, decrypted_dex_path, aes_key, aes_iv)

    recompiled_apk_path = 'C:\\Users\\HP\\Desktop\\sandbox\\recompiled.apk'
    recompile_apk(decompiled_dir, recompiled_apk_path)

    mobsf_url = 'http://127.0.0.1:8000/'
    api_key = '816b6bbd700d4dd27eb9ed1da4017e3023284a1ebd56683f9eeb21962463fa62'

    static_analysis_results = upload_and_scan(recompiled_apk_path, mobsf_url, api_key)
    if static_analysis_results:
        print(static_analysis_results)
