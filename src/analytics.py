import time
from collections import deque
import cv2
import numpy as np
import supervision as sv

class TrafficAnalytics:
    def __init__(self, frame_width: int, frame_height: int, line_y_ratio: float = 0.6, window_seconds: int = 60):
        self.line_y = int(frame_height * line_y_ratio)
        
        # Posiciona a linha virtual horizontal
        start_point = sv.Point(0, self.line_y)
        end_point = sv.Point(frame_width, self.line_y)
        
        self.line_zone = sv.LineZone(start=start_point, end=end_point)
        self.line_annotator = sv.LineZoneAnnotator(thickness=2, text_scale=0.6, text_thickness=1)
        
        self.window_seconds = window_seconds
        self.timestamps = deque()

    def update(self, detections: sv.Detections):
        prev_total = self.line_zone.in_count + self.line_zone.out_count
        
        # Processa cruzamentos da linha
        self.line_zone.trigger(detections=detections)
        
        current_total = self.line_zone.in_count + self.line_zone.out_count
        new_crossings = current_total - prev_total
        
        now = time.time()
        for _ in range(new_crossings):
            self.timestamps.append(now)

        # Remove os registos com mais de 60 segundos
        while self.timestamps and (now - self.timestamps[0] > self.window_seconds):
            self.timestamps.popleft()

        return current_total, len(self.timestamps)

    def draw_dashboard(self, frame: np.ndarray, total_count: int, cpm: int) -> np.ndarray:
        # Desenha a linha virtual na imagem
        annotated = self.line_annotator.annotate(frame=frame, line_counter=self.line_zone)
        
        # Desenha o painel de estatísticas no canto superior esquerdo
        cv2.rectangle(annotated, (10, 10), (370, 110), (0, 0, 0), -1)
        cv2.putText(annotated, f"Total Contado: {total_count}", (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(annotated, f"Fluxo (CPM): {cpm} veic/min", (20, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return annotated