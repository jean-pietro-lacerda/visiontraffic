import cv2
from src.capture import VideoCaptureManager
from src.detector import TrafficDetector
from src.analytics import TrafficAnalytics

VIDEO_PATH = "data/transito.mp4"
MODEL_PATH = "models/yolov8m.pt"

def main():
    # Inicializa os componentes do sistema
    capture = VideoCaptureManager(video_path=VIDEO_PATH, target_size=(1280, 720))
    detector = TrafficDetector(model_path=MODEL_PATH)
    analytics = TrafficAnalytics(frame_width=1280, frame_height=720, line_y_ratio=0.6)

    print("Sistema de Análise de Tráfego iniciado. Pressione 'q' na janela para encerrar.")

    while True:
        success, frame = capture.read_frame()
        if not success:
            print("Fim do vídeo ou falha na leitura.")
            break

        # Processamento de detecção e atribuição de IDs
        detections = detector.process_frame(frame)
        
        # Desenha caixas e rótulos
        annotated_frame = detector.annotate_frame(frame, detections)

        # Atualiza a contagem da linha e calcula o fluxo CPM
        total_count, cpm = analytics.update(detections)

        # Desenha a linha virtual e o painel na tela
        final_frame = analytics.draw_dashboard(annotated_frame, total_count, cpm)

        # Exibição do resultado
        cv2.imshow("Monitorização de Tráfego em Tempo Real", final_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()