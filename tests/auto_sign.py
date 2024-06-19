import subprocess
import os
import requests
from Cryptodome.Cipher import AES
import glob

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
        # DEX 파일이 위치한 디렉토리를 기반으로 복호화된 DEX 파일의 저장 경로 설정
        dex_dir = os.path.dirname(dex_file)
        dex_base_name = os.path.basename(dex_file)
        # 'kill' 부분을 'decrypted'로 대체하여 복호화된 DEX 파일의 이름 생성
        decrypted_dex_name = dex_base_name.replace('kill', 'decrypted_kill')
        decrypted_dex_path = os.path.join(dex_dir, decrypted_dex_name)
        decrypt_dex(dex_file, decrypted_dex_path, aes_key, aes_iv)


def decrypt_dex(encrypted_dex_path, decrypted_dex_path, aes_key, aes_iv):
    # DEX 파일 복호화
    try:
        with open(encrypted_dex_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
        decrypted_data = cipher.decrypt(encrypted_data)
        with open(decrypted_dex_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)
        print(f"DEX 복호화 성공: {encrypted_dex_path} -> {decrypted_dex_path}")
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

def upload_and_scan(file_path, mobsf_url, api_key):
    # MobSF에 파일 업로드 및 스캔 요청
    headers = {'Authorization': api_key}
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
        response = requests.post(f'{mobsf_url}/api/v1/upload', files=files, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            print("업로드 및 스캔 요청 성공")
            print_response_summary(response_data)
            return response_data['hash']
        else:
            print("업로드 및 스캔 요청 실패")
            return None

def start_scan(mobsf_url, api_key, file_hash):
    # MobSF에서 스캔 시작
    headers = {'Authorization': api_key}
    data = {'hash': file_hash}
    response = requests.post(f'{mobsf_url}/api/v1/scan', headers=headers, data=data)
    if response.status_code == 200:
        response_data = response.json()
        print("스캔 시작 성공")
        print_response_summary(response_data)
        return response_data.get('scan_id')
    else:
        print("스캔 시작 실패")
        return None

def get_scan_results(mobsf_url, api_key, scan_id):
    # MobSF로부터 스캔 결과 가져오기
    headers = {'Authorization': api_key}
    params = {'hash': scan_id}
    response = requests.get(f'{mobsf_url}/api/v1/report_json', headers=headers, params=params)
    if response.status_code == 200:
        response_data = response.json()
        print("스캔 결과 성공적으로 받아옴")
        return response_data
    else:
        print("스캔 결과 가져오기 실패")
        return None
    
def print_response_summary(response_data):
    # 응답 데이터 요약 정보 출력
    if 'scan_id' in response_data:
        print(f"스캔 ID: {response_data['scan_id']}")
    if 'hash' in response_data:
        print(f"파일 해시: {response_data['hash']}")
    if 'error' in response_data:
        print(f"에러 메시지: {response_data['error']}")

def download_pdf_report(mobsf_url, api_key, scan_id, output_dir):
    # MobSF로부터 PDF 보고서 다운로드
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
        print("PDF 보고서 다운로드 실패")


if __name__ == "__main__":
    apk_path = 'C:\\Users\\HP\\Desktop\\sandbox\\sample.apk'
    decompiled_dir = 'C:\\Users\\HP\\Desktop\\sandbox\\decompiled_apk'
    aes_key = b'dbcdcfghijklmaop'
    aes_iv = b'\x92\x10,\x19\xc4,@\xd1 \xa3\xbe\xa1\xc9_\xbd`'
    output_dir = 'C:\\Users\\HP\\Desktop\\sandbox'
    mobsf_url = 'http://127.0.0.1:8000'
    api_key = '816b6bbd700d4dd27eb9ed1da4017e3023284a1ebd56683f9eeb21962463fa62'

    # Keystore 정보 입력
    keystore_path = 'C:\\Users\\HP\\Desktop\\sandbox\\cloudwoon.keystore' #keystore 위치
    keystore_password = 'cloudwoon'  # Keystore 비밀번호
    key_alias = 'cloudwoon'  # 키 별칭

    # 메인 APK 디컴파일
    decompile_apk(apk_path, decompiled_dir)
    # 중첩된 APK 찾기 및 디컴파일, 'kill'로 시작하는 DEX 파일 처리
    find_nested_apks_and_decompile(decompiled_dir)
    process_dex_files(decompiled_dir)
    # MobSF 작업 수행
    
    recompiled_apk_path = os.path.join(output_dir, 're_sample.apk')
    recompile_apk(decompiled_dir, recompiled_apk_path, keystore_path, keystore_password, key_alias)

    file_hash = upload_and_scan(recompiled_apk_path, mobsf_url, api_key)
    if file_hash:
        scan_id = start_scan(mobsf_url, api_key, file_hash)
        if scan_id:
            scan_results = get_scan_results(mobsf_url, api_key, scan_id)
            if scan_results:
                print("스캔 결과:", scan_results)
                download_pdf_report(mobsf_url, api_key, scan_id, output_dir)