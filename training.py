from ultralytics import YOLO

# Load model paling akurat
model = YOLO('yolov8n.pt')

# Training
model.train(
    data='/home/iqbal/Downloads/Crime.v1i.yolov8/data.yaml',
    epochs=20,
    imgsz=640,
    batch=16,   # Sesuaikan dengan kapasitas GPU
    device=0    # Gunakan GPU
)