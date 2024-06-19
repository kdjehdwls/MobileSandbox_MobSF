# static analayz 자동화
# 대체 왜 apk not found라고 뜨는가
# bool문제는 어떻게 해결하는가 엿같아요
# NOT FOUND APK FILE
# Traceback (most recent call last):
#   File "C:\Users\vboxuser\Desktop\sandbox\result\static_api.py", line 149, in <module>
#     decomplied_dir = apk_process(apk_file_path)
#   File "C:\Users\vboxuser\Desktop\sandbox\result\static_api.py", line 69, in apk_process
#     decompiled_dir = apk_file + "_decomplied"
# TypeError: unsupported operand type(s) for +: 'bool' and 'str'


import requests
import os
import subprocess
from Cryptodome.Cipher import AES
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

SERVER = "http://127.0.0.1:8000"
FILE = 'sample.apk'
APIKEY = '62662492381905eba7def5c73202dea82f14eb501511d426f8d3f8699d10f8f8'


def upload():
    """Upload File"""
    print("Uploading file")
    multipart_data = MultipartEncoder(fields={'file': (FILE, open(FILE, 'rb'), 'application/octet-stream')})
    headers = {'Content-Type': multipart_data.content_type, 'Authorization': APIKEY}
    response = requests.post(SERVER + '/api/v1/upload', data=multipart_data, headers=headers)
    print(response.text)
    return response.text


def scan(data):
    """Scan the file"""
    print("Scanning file")
    post_dict = json.loads(data)
    headers = {'Authorization': APIKEY}
    response = requests.post(SERVER + '/api/v1/scan', data=post_dict, headers=headers)
    print(response.text)


# apk파일 찾기
def find_apk_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".apk"):
                apk_file_path = os.path.join(root, file)
                print("FOUND APK FILE")
                print(apk_file_path)
                return apk_file_path
            else:
                print("NOT FOUND APK FILE")
                print(file)
    return False

# apk파일 디컴파일
def apk_process(apk_file):
    decompiled_dir = apk_file + "_decomplied"
    apktool_path = 'C:\Windows\apktool.bat'
    print(f'decomplied_dir: {decompiled_dir}')
    try:
        # APKTool을 사용하여 APK 파일을 디컴파일합니다.
        subprocess.run([apktool_path, "d", apk_file, "-o", decompiled_dir], check=True)
        print("APK decomplie complete")
        return decompiled_dir
    except subprocess.CalledProcessError as e:
        print(f"APK decomplie fail: {e}")
        return None

# AES 복호화
def decrypt_aes_ecb(encrypted_data, key):
    # AES-128/ECB 모드를 사용하여 데이터를 복호화합니다.
    cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data

# 복호화수행
def decrypt_dex_file(encrypted_dex_path):
    key = b'dbcdcfghijklmaop'
    decrypted_dex_path = './decrypt_dex_file.dex'
    print(f'decrypted_dex_path: {decrypted_dex_path}')
    try:
        with open(encrypted_dex_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        
        decrypted_data = decrypt_aes_ecb(encrypted_data, key)
        
        # 복호화된 데이터를 파일로 저장합니다.
        with open(decrypted_dex_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)
            
        print(f"{decrypted_file} decrypted complete")
        return True
    except Exception as e:
        print(f"Decrypting Error: {e}")
        return False

def sign_apk(unsigned_apk_path):
    signed_apk_path = 'C:\Users\vboxuser\.MobSF\output_app_signed.apk'  # 서명된 APK 파일 경로
    keystore_path = 'C:\Users\vboxuser\test\my-release.keystore'  # 키스토어 파일 경로
    keystore_pass = "i'mbob"  # 키스토어 비밀번호
    alias_name = 'alias_name'  # 키 별칭
    
    try:
        # jarsigner를 사용하여 APK 파일에 서명합니다.
        subprocess.run(["jarsigner", "-verbose", "-sigalg", "SHA1withRSA", "-digestalg", "SHA1",
                        "-keystore", keystore_path, "-storepass", keystore_pass,
                        unsigned_apk_path, alias_name,
                        "-signedjar", signed_apk_path], check=True)
        print("APK signing complete")
    except subprocess.CalledProcessError as e:
        print(f"APK signing fail: {e}")
    
def repackage_apk(decrpyted_app_dir):
    output_apk_path = 'C:\Users\HP\Desktop\sandbox\repack_sample.apk'
    try:
        # APKTool을 사용하여 APK 파일을 리패키징합니다.
        subprocess.run(["apktool", "b", decrpyted_app_dir, "-o", output_apk_path], check=True)
        print("APK repackaging complete")
        sign_apk(output_apk_path)
    except subprocess.CalledProcessError as e:
        print(f"APK repackaging fail: {e}")

import glob
# 암호화된 dex파일
def is_encrypted_dex(decomplied_dir):
    dex_files = glob.glob(os.path.join(decomplied_dir, '*.dex'))
    
    if not dex_files:
        print("Not found dex file")
        return False
    
    for dex_file_path in dex_files:
        try:
                    
            with open(dex_file_path, 'rb') as file:
                header = file.read(4)
                if header.startswith(b'dex\n'):
                    print(f"found encrypte dex file {dex_file_path}")
                    decrypt_dex_file(dex_file_path)
                    repackage_apk(dex_file_path)
            return True
        except PermissionError:
            print(f"{dex_file_path} permission denid")
            return False
        except Exception as e:
            print(f"{dex_file_path} file error\n{e}")
            return False

# main code
RESP = upload()
scan(RESP)
directory = 'C:\Users\HP\Desktop\sandbox'
apk_file_path = find_apk_files(directory)
decomplied_dir = apk_process(apk_file_path)
is_encrypted_dex(decomplied_dir)
# pdf(RESP)
#delete(RESP)
