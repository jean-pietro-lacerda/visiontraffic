import numpy as np
from ultralytics import YOLO
import supervision as sv

class TrafficDetector:
    def __init__(self, model_path: str = "models/yolov8m.pt", vehicle_classes=[2, 3, 5, 7]):
        self.model = YOLO(model_path)
        self.vehicle_classes = vehicle_classes

        # Anotadores gráficos da biblioteca Supervision
        self.box_annotator = sv.BoxAnnotator(thickness=2)
        self.label_annotator = sv.LabelAnnotator(text_scale=0.5, text_padding=3)

    def process_frame(self, frame: np.ndarray) -> sv.Detections:
        # Executa o tracking mantendo a persistência de IDs
        results = self.model.track(
            frame, 
            persist=True, 
            classes=self.vehicle_classes, 
            verbose=False
        )[0]

        # Converte para a estrutura do Supervision
        detections = sv.Detections.from_ultralytics(results)

        if results.boxes.id is not None:
            detections.tracker_id = results.boxes.id.cpu().numpy().astype(int)

        return detections

    def annotate_frame(self, frame: np.ndarray, detections: sv.Detections) -> np.ndarray:
        labels = []
        if detections.tracker_id is not None:
            for class_id, tracker_id in zip(detections.class_id, detections.tracker_id):
                class_name = self.model.names[class_id]
                labels.append(f"#{tracker_id} {class_name}")

        annotated = self.box_annotator.annotate(scene=frame, detections=detections)
        annotated = self.label_annotator.annotate(scene=annotated, detections=detections, labels=labels)
        return annotated