from torchcam.methods import GradCAM, GradCAMpp, SmoothGradCAMpp, ScoreCAM, SSCAM
from torchcam.utils import overlay_mask

from model.modeling.model import Model

import torch
from torchvision.io.image import read_image
from torchvision.transforms.functional import normalize, resize, to_pil_image

def generate_heatmap(diagnose_type, heatmap_type, image_path):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    class_num = {"糖尿病视网膜病病变分级": 5, "青光眼": 1, "多疾病": 14}
    weights_path = {"糖尿病视网膜病病变分级": "diabetic retinopathy.pth", "青光眼": "glaucoma.pth", "多疾病": "multiple diseases.pth"}

    whole_model = Model(vision_type='resnet_v2', bert_type='./Bio_ClinicalBERT',
                        from_checkpoint=False, vision_pretrained=True).to(device)
    whole_model.classifier = torch.nn.Linear(512, class_num[diagnose_type], bias=True).to(device)
    whole_model.load_from_pretrained("./checkpoint/" + weights_path[diagnose_type])

    image = read_image(image_path).to(torch.float32)
    input_tensor = normalize(resize(image, (224, 224)), mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) / 255.
    input_tensor = input_tensor.to(device)

    model = whole_model.vision_model
    model.eval()

    if heatmap_type == "GradCAM":
        cam_extractor = GradCAM(model=model, target_layer=[model.model.layer4])
    elif heatmap_type == "GradCAM++":
        cam_extractor = GradCAMpp(model=model, target_layer=[model.model.layer4])
    elif heatmap_type == "SmoothGradCAM++":
        cam_extractor = SmoothGradCAMpp(model=model, target_layer=[model.model.layer4])
    elif heatmap_type == "ScoreCAM":
        cam_extractor = ScoreCAM(model=model, target_layer=[model.model.layer4])
    elif heatmap_type == "SSCAM":
        cam_extractor = SSCAM(model=model, target_layer=[model.model.layer4])
    else:
        return
    
    out = model(input_tensor.unsqueeze(0))
    out = whole_model.classifier(out)

    activation_map = cam_extractor(out.squeeze(0).argmax().item(), out)
    result = overlay_mask(to_pil_image(image), to_pil_image(activation_map[0].squeeze(0), mode='F'), alpha=0.7)

    image_name = image_path.split("/")[-1]
    suffix = image_name.split(".")[-1]
    new_image_path = "./热图/" + image_name.split(".")[0] + "_" + heatmap_type + "." + suffix
    result.save(new_image_path)