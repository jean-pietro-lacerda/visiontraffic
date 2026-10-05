import cv2

class VideoCaptureManager:
    def __init__(self, video_path: str, target_size=(1280, 720)):
        self.video_path = video_path
        self.target_size = target_size
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise ValueError(f"Não foi possível abrir o vídeo no caminho: {video_path}")

    def read_frame(self):
        success, frame = self.cap.read()
        if not success:
            return False, None
        
        if self.target_size:
            frame = cv2.resize(frame, self.target_size)
        
        return True, frame

    def release(self):
        self.cap.release()