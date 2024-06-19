# class MobSF_API:
#     # 기존의 __init__, upload, scan 등의 메소드는 생략합니다...

#     def dynamic_tls_ssl_test(self):
#         """동적 분석 중 TLS/SSL 보안 테스트 수행"""
#         if not self.scan_hash:
#             print("파일이 업로드되지 않았거나 해시를 찾을 수 없습니다.")
#             return
#         print("TLS/SSL 보안 테스트 수행 중...")
#         headers = {'Authorization': self.api_key}
#         data = {'hash': self.scan_hash}
#         response = requests.post(f'{self.server}/api/v1/android/tls_tests', data=data, headers=headers)
#         if response.status_code == 200:
#             print("TLS/SSL 보안 테스트가 성공적으로 완료되었습니다.")
#             results = response.json()
#             print(json.dumps(results, indent=4))
#         else:
#             print("TLS/SSL 보안 테스트 수행에 실패했습니다.")

#     # 기존의 dynamic_analysis_stop, dynamic_analysis_activity_test 등의 메소드는 생략합니다...

# def main():
#     server_url = 'http://127.0.0.1:8000'
#     api_key = '여러분의 MobSF API 키를 여기에 입력하세요'
#     file_path = '분석하고자 하는 APK 파일의 경로를 여기에 입력하세요'

#     mobSF = MobSF_API(server_url, api_key, file_path)

#     # 파일 업로드
#     upload_result = mobSF.upload()
#     if 'hash' in upload_result:
#         print("파일이 성공적으로 업로드되었습니다. 스캔을 시작합니다...")
        
#         # 정적 분석 시작
#         mobSF.scan()
        
#         # 동적 분석 설정
#         dynamic_analysis_result = mobSF.dynamic_analysis_setting()
#         if dynamic_analysis_result.get("status") == "ok":
#             # 동적 분석 중 TLS/SSL 보안 테스트 수행
#             mobSF.dynamic_tls_ssl_test()

#             # 동적 분석 중단
#             mobSF.dynamic_analysis_stop()

#             # 보고서 생성
#             time.sleep(5)  # 동적 분석이 완전히 완료될 때까지 기다림
#             mobSF.pdf()
#             mobSF.json_resp()

# if __name__ == "__main__":
#     main()
