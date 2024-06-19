import subprocess
import os
import requests
from Cryptodome.Cipher import AES

def decompile_apk(apk_path, output_dir):
    try:
        subprocess.run(['C:\\Windows\\apktool.bat', 'd', apk_path, '-o', output_dir, '-f'], input=b'\n', check=True)
        print("APK 디컴파일 성공")
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
        print("DEX 복호화 성공")
    except Exception as e:
        print(f"DEX 복호화 중 에러 발생: {e}")

def recompile_apk(decompiled_dir, output_apk_path):
    try:
        subprocess.run(['C:\\Windows\\apktool.bat', 'b', decompiled_dir, '-o', output_apk_path, '-f'], input=b'\n', check=True)
        print("APK 재컴파일 성공")
    except subprocess.CalledProcessError as e:
        print(f"APK 재컴파일 중 에러 발생: {e}")

def upload_and_scan(file_path, mobsf_url, api_key):
    headers = {'Authorization': api_key}
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
        response = requests.post(f'{mobsf_url}/api/v1/upload', files=files, headers=headers)

        if response.status_code == 200:
            print("업로드 성공:", response.json())
            return response.json()['hash']
        else:
            print("업로드 실패, 상태 코드:", response.status_code)
            return None

def start_scan(mobsf_url, api_key, file_hash):
    headers = {'Authorization': api_key}
    data = {'hash': file_hash}
    response = requests.post(f'{mobsf_url}/api/v1/scan', headers=headers, data=data)

    if response.status_code == 200:
        print("스캔 시작 성공:", response.json())
        return response.json()['scan_id']
    else:
        print("스캔 시작 실패, 상태 코드:", response.status_code)
        return None

def get_scan_results(mobsf_url, api_key, scan_id):
    headers = {'Authorization': api_key}
    params = {'hash': scan_id}
    response = requests.get(f'{mobsf_url}/api/v1/report_json', headers=headers, params=params)

    if response.status_code == 200:
        print("스캔 결과 성공적으로 받아옴")
        return response.json()
    else:
        print("스캔 결과 가져오기 실패, 상태 코드:", response.status_code)
        return None

def download_pdf_report(mobsf_url, api_key, scan_id, output_dir):
    headers = {'Authorization': api_key}
    data = {'hash': scan_id}
    response = requests.post(f'{mobsf_url}/api/v1/download_pdf', headers=headers, data=data, stream=True)

    if response.status_code == 200:
        output_path = os.path.join(output_dir, f'{scan_id}.pdf')
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"PDF 보고서 {output_path}로 다운로드 완료")
    else:
        print("PDF 보고서 다운로드 실패, 상태 코드:", response.status_code)
        print("응답 내용:", response.text)

if __name__ == "__main__":
    apk_path = 'C:\\Users\\HP\\Desktop\\sandbox\\sample.apk'
    decompiled_dir = 'C:\\Users\\HP\\Desktop\\sandbox\\decompiled_apk'
    aes_key = b'dbcdcfghijklmaop'
    aes_iv = b'\x92\x10,\x19\xc4,@\xd1 \xa3\xbe\xa1\xc9_\xbd`'
    output_dir = 'C:\\Users\\HP\\Desktop\\sandbox'

    decompile_apk(apk_path, decompiled_dir)
    encrypted_dex_path = os.path.join(decompiled_dir, 'kill-classes.dex')
    decrypted_dex_path = os.path.join(decompiled_dir, 'classes2.dex')
    decrypt_dex(encrypted_dex_path, decrypted_dex_path, aes_key, aes_iv)
    recompiled_apk_path = os.path.join(output_dir, 'recompiled.apk')
    recompile_apk(decompiled_dir, recompiled_apk_path)

    mobsf_url = 'http://127.0.0.1:8000'
    api_key = '816b6bbd700d4dd27eb9ed1da4017e3023284a1ebd56683f9eeb21962463fa62'

    file_hash = upload_and_scan(recompiled_apk_path, mobsf_url, api_key)
    if file_hash:
        scan_id = start_scan(mobsf_url, api_key, file_hash)
        if scan_id:
            scan_results = get_scan_results(mobsf_url, api_key, scan_id)
            download_pdf_report(mobsf_url, api_key, scan_id, output_dir)
