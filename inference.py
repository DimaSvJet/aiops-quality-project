import torch
from torchvision import transforms
from PIL import Image
import sys

model = torch.jit.load("model/traced_model.pt")

model.eval()

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor()
])


def predict(image_path):
    image = Image.open(image_path).convert("RGB")
    input_tensor = preprocess(image).unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)
        top3_values, top3_indices = torch.topk(output, 3)
        for i in range(3):
            class_id = top3_indices[0][i].item()
            score = top3_values[0][i].item()
            print(f"Top {i+1}: class ID={class_id}, score={score}")


@app.post("/predict")
