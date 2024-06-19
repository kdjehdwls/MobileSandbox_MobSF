import subprocess
import os
import requests
from Cryptodome.Cipher import AES

# APKTool로 APK 디컴파일
def decompile_apk(apk_path, output_dir):
    subprocess.run(['C:\\Windows\\apktool.bat', 'd', apk_path, '-o', output_dir, '-r', '-s'], check=True)


# DEX 파일 복호화
def decrypt_dex(encrypted_dex_path, decrypted_dex_path, aes_key, aes_iv):
    with open(encrypted_dex_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()

    cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    decrypted_data = cipher.decrypt(encrypted_data)

    with open(decrypted_dex_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)

# APKTool로 APK 재컴파일
def recompile_apk(decompiled_dir, output_apk_path):
    subprocess.run(['C:\\Windows\\apktool.bat', 'b', decompiled_dir, '-o', output_apk_path], check=True)

# MobSF에 파일 업로드 및 정적 분석 요청
def upload_and_scan(file_path, mobsf_url, api_key):
    files = {'file': (file_path, open(file_path, 'rb'))}
    headers = {'Authorization': api_key}
    response = requests.post(mobsf_url + 'upload', files=files, headers=headers)
    scan_id = response.json()['scan_id']

    data = {'scan_type': 'apk', 'file_name': file_path, 'scan_id': scan_id}
    response = requests.post(mobsf_url + 'scan', data=data, headers=headers)
    return response.json()

# 메인 프로세스
if __name__ == "__main__":
    apk_path = 'C:\\Users\\HP\\Desktop\\sandbox\\sample.apk'  # Windows 경로 문자열 수정
    decompiled_dir = 'C:\\Users\\HP\\Desktop\\sandbox\\decompiled_apk'
    aes_key = b'dbcdcfghijklmaop'
    aes_iv = b'\x92\x10,\x19\xc4,@\xd1 \xa3\xbe\xa1\xc9_\xbd`'

    # APK 디컴파일
    decompile_apk(apk_path, decompiled_dir)

    # DEX 파일 찾기 (예시로 'kill-classes.dex'를 사용)
    encrypted_dex_path = os.path.join(decompiled_dir, 'kill-classes.dex')
    decrypted_dex_path = os.path.join(decompiled_dir, 'classes2.dex')

    # DEX 파일 복호화
    decrypt_dex(encrypted_dex_path, decrypted_dex_path, aes_key, aes_iv)

    # APK 재컴파일
    recompiled_apk_path = 'C:\\Users\\HP\\Desktop\\sandbox\\recompiled.apk'
    recompile_apk(decompiled_dir, recompiled_apk_path)

    # MobSF 설정 (URL과 API 키 필요)
    mobsf_url = 'http://127.0.0.1:8000/'
    api_key = '816b6bbd700d4dd27eb9ed1da4017e3023284a1ebd56683f9eeb21962463fa62'

    # MobSF에 업로드 및 정적 분석
    static_analysis_results, _ = upload_and_scan(recompiled_apk_path, mobsf_url, api_key)

    # 정적 분석 결과 출력
    print(static_analysis_results)
