import cv2
import numpy as np
import requests
import threading
import time

class VideoStreamClient:
    def __init__(self, server_url):
        """비디오 스트림 클라이언트 초기화""" # [cite: 149]
        # Args: server_url (str): 서버 스트림 URL (예: 'http://192.168.5.1:5000/stream') [cite: 150, 151]
        self.server_url = server_url # [cite: 152]
        self.stream_active = False # [cite: 153]
        self.stream_thread = None # [cite: 154]
        self.latest_frame = None # [cite: 155]
        self.frame_lock = threading.Lock() # [cite: 156, 157]
        
    def start_stream(self):
        """스트림 수신 시작""" # [cite: 159]
        if self.stream_active: # [cite: 160]
            print("이미 스트림이 활성화되어 있습니다.") # [cite: 161]
            return
        self.stream_active = True # [cite: 162]
        self.stream_thread = threading.Thread(target=self._receive_stream) # [cite: 163]
        self.stream_thread.daemon = True # [cite: 164]
        self.stream_thread.start() # [cite: 165]
        
    def stop_stream(self):
        """스트림 수신 중지""" # [cite: 167]
        self.stream_active = False # [cite: 168]
        if self.stream_thread: # [cite: 169]
            self.stream_thread.join(timeout=1.0) # [cite: 170]
            
    def get_latest_frame(self):
        """최신 수신된 프레임 반환""" # [cite: 172]
        with self.frame_lock: # [cite: 173]
            if self.latest_frame is None: # [cite: 174]
                return None # [cite: 175]
            return self.latest_frame.copy() # [cite: 176]
            
    def _receive_stream(self):
        """비디오 스트림 수신 및 처리하는 내부 메서드""" # [cite: 180]
        try:
            # 스트림에 연결
            response = requests.get(self.server_url, stream=True) # [cite: 181, 182, 183]
            if response.status_code != 200: # [cite: 184]
                print(f"서버 연결 실패: {response.status_code}") # [cite: 185]
                self.stream_active = False # [cite: 186, 187]
                return # [cite: 188]
                
            # MJPEG 스트림의 바이트 데이터
            bytes_data = bytes() # [cite: 189, 190]
            
            # 스트림 처리 루프
            for chunk in response.iter_content(chunk_size=1024): # [cite: 191, 192]
                bytes_data += chunk # [cite: 193]
                
                # JPEG 시작 바이트(\xff\xd8)와 끝 바이트(\xff\xd9) 찾기
                a = bytes_data.find(b'\xff\xd8') # [cite: 195, 202]
                b = bytes_data.find(b'\xff\xd9') # [cite: 196, 203]
                
                if a != -1 and b != -1: # [cite: 197]
                    # 완전한 JPEG 프레임 찾음
                    jpg = bytes_data[a:b+2] # [cite: 198, 199]
                    bytes_data = bytes_data[b+2:] # [cite: 200]
                    
                    # JPEG 바이트 데이터를 이미지로 디코딩
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR) # [cite: 194, 201, 204]
                    
                    # 최신 프레임 저장
                    with self.frame_lock: # [cite: 205, 206]
                        self.latest_frame = frame # [cite: 207]
                        
                # 스트림이 비활성화되면 종료
                if not self.stream_active: # [cite: 208, 209]
                    break # [cite: 210]
        except Exception as e:
            print(f"스트림 수신 중 오류 발생: {e}") # [cite: 211, 212]
        finally:
            self.stream_active = False # [cite: 213, 214, 215]

# 사용 예시
if __name__ == "__main__": # [cite: 216, 217, 218]
    # 서버 URL (본인의 라즈베리파이 실제 IP 주소로 변경 필수)
    server_url = "http://192.168.0.173:5000/stream" # [cite: 135, 219, 220]
    
    # 클라이언트 생성 및 시작
    client = VideoStreamClient(server_url) # [cite: 221, 222, 223]
    client.start_stream() # [cite: 224]
    
    # 프레임 표시 루프
    try:
        while True: # [cite: 225, 227]
            frame = client.get_latest_frame() # [cite: 228]
            if frame is not None: # [cite: 229]
                cv2.imshow("Jetcobot Camera Stream", frame) # [cite: 231]
                
            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'): # [cite: 232, 233]
                break # [cite: 234]
    except KeyboardInterrupt:
        print("종료 중...") # [cite: 235, 236]
    finally:
        client.stop_stream() # [cite: 237, 238]
        cv2.destroyAllWindows() # [cite: 239]