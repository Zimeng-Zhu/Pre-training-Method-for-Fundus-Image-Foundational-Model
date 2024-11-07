from model.modeling.model import Model

import torch
import numpy as np
from PIL import Image
from torchvision.transforms import Resize

from torchvision.io.image import read_image
from torchvision.transforms.functional import normalize, resize

def load_image(image_path):
    image = np.array(Image.open(image_path), dtype=float)
    if np.max(image) > 1:
        image /= 255

    if len(image.shape) > 2:
        image = np.transpose(image, (2, 0, 1))
    else:
        image = np.expand_dims(image, 0)

    if image.shape[0] > 3:
        image = image[1:, :, :]
    if image.shape[0] < 3:
        image = np.repeat(image, 3, axis=0)

    return image

def scale_image(image, size=(512, 512)):
    image = torch.tensor(image)

    transforms = torch.nn.Sequential(Resize(size))
    if image.shape[-1] == image.shape[-2]:
        image = transforms(image)
    else:
        sizes = image.shape[-2:]
        max_size = max(sizes)
        scale = max_size / size[0]
        image = Resize((int(image.shape[-2] / scale), int((image.shape[-1] / scale))))(image)
        image = torch.nn.functional.pad(image, (0, size[0] - image.shape[-1], 0, size[1] - image.shape[-2], 0, 0))

    return image

def diagnose(diagnose_type, image_path):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    class_num = {"糖尿病视网膜病病变分级": 5, "青光眼": 1, "多疾病": 14}
    class_name = {"糖尿病视网膜病病变分级": {0: "no diabetic retinopathy", 1: "mild diabetic retinopathy",
                                           2: "moderate diabetic retinopathy", 3: "severe diabetic retinopathy",
                                           4: "proliferative diabetic retinopathy"},
                  "青光眼": {0: "no glaucoma", 1: "glaucoma"},
                  "多疾病": {0: 'no diabetic retinopathy', 1: 'microaneurysm', 2: 'retinal hemorrhage',
                            3: 'hard exudate', 4: 'retinal edema', 5: 'more than three small soft exudates',
                            6: 'neovascularization', 7: 'preretinal haemorrhage', 8: 'fibrovascular proliferativemembrane',
                            9: 'tractionalretinaldetachment', 10: 'soft exudate', 11: 'varicose veins',
                            12: 'intraretinal microvascular abnormality', 13: 'non-perfusion area over one disc area'}}
    weights_path = {"糖尿病视网膜病病变分级": "diabetic retinopathy.pth", "青光眼": "glaucoma.pth", "多疾病": "multiple diseases.pth"}

    whole_model = Model(vision_type='resnet_v2', bert_type='./Bio_ClinicalBERT',
                        from_checkpoint=False, vision_pretrained=True).to(device)
    whole_model.classifier = torch.nn.Linear(512, class_num[diagnose_type], bias=True).to(device)
    whole_model.load_from_pretrained("./checkpoint/" + weights_path[diagnose_type])

    # image = load_image(image_path)
    # image = scale_image(image)
    # image.to(torch.float32).to(device)

    image = read_image(image_path).to(torch.float32)
    input_tensor = normalize(resize(image, (224, 224)) / 255., mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    input_tensor = input_tensor.to(device)

    X = whole_model.vision_model(input_tensor.unsqueeze(0))
    score = whole_model.classifier(X)

    if score.shape[-1] == 1:
        score = torch.sigmoid(score)
        score = torch.concat([1 - score, score], -1)[0]
    else:
        score = torch.softmax(score, -1)[0]

    text = ""
    for c in range(len(class_name[diagnose_type])):
        disease = class_name[diagnose_type][c]
        possibility = score[c].item()
        text += disease + ": " + str(round(possibility * 100, 2)) + "%\n"

    return text