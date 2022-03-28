import torch
from mtcnn import MTCNN
from model import ViViT
import cv2
import numpy as np
from torchvision import transforms

face_detector = MTCNN()
engagement_detector = ViViT()
engagement_detector.load_state_dict(torch.load('engagement.pth'), strict=False)
engagement_detector.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 人脸检测
def detect_crop_face_base_mtcnn(image):
    height, width, channel = image.shape
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    faces = face_detector.detect_faces(imageRGB)
    if len(faces) != 0:
        # It may contains several faces, we regard the biggest face as the target face
        x_temp = y_temp = w_temp = h_temp = 0
        for k, d in enumerate(faces):
            x, y, w, h = d["box"]
            if w * h > w_temp * h_temp:
                x_temp = x
                y_temp = y
                w_temp = w
                h_temp = h
                nose_temp = d["keypoints"]["nose"]
        x = x_temp
        y = y_temp
        w = w_temp
        h = h_temp
        nose = nose_temp

        # resize the face to the target size without changing the facial emotion
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if True:
            nose_x, nose_y = nose
            if nose_x > x + w * 0.5:
                margin = nose_x - x
                if x + 2 * margin > width:
                    margin = width - nose_x
                    x = width - margin * 2
            else:
                margin = x + w - nose_x
                if nose_x - margin < 0:
                    margin = nose_x
                    x = 0
                else:
                    x = x + w - 2 * margin
            w = 2 * margin
            if nose_y > y + h * 0.5:
                margin = nose_y - y
                if y + 2 * margin > height:
                    margin = height - nose_y
                    y = height - margin * 2
            else:
                margin = y + h - nose_y
                if nose_y - margin < 0:
                    margin = nose_y
                    y = 0
                else:
                    y = y + h - 2 * margin
            h = 2 * margin

        if w > h:
            margin = w - h
            half_margin_1 = int(margin / 2)
            half_margin_2 = margin - half_margin_1
            if y - half_margin_1 < 0 or y + h + half_margin_2 > height:
                if y - half_margin_1 < 0:
                    face_crop = image[y:y + h + margin, x:x + w]
                else:
                    face_crop = image[y - margin:y + h, x:x + w]
            else:
                face_crop = image[y - half_margin_1:y + h + half_margin_2, x:x + w]
        else:
            if h > w:
                margin = h - w
                half_margin_1 = int(margin / 2)
                half_margin_2 = margin - half_margin_1
                if x - half_margin_1 < 0 or x + w + half_margin_2 > width:
                    if x - half_margin_1 < 0:
                        face_crop = image[y:y + h, x:x + w + margin]
                    else:
                        face_crop = image[y:y + h, x - margin:x + w]
                else:
                    face_crop = image[y:y + h, x - half_margin_1:x + w + half_margin_2]
            else:
                face_crop = image[y:y + h, x:x + w]

        face_crop = cv2.resize(face_crop, (224, 224))
        # cv2.imwrite("MTCNN/" + person + "_" + num + "crop.jpg", face_crop)

        return face_crop

    else:
        image = np.zeros((224, 224, 3))
        return image

# 检测专注度
def detect_engagement(faces):
    out = engagement_detector(faces).squeeze()
    out = torch.softmax(out, dim=0)
    print(torch.argmax(out).item(), out[torch.argmax(out)].item())
    return torch.argmax(out).item(), out[torch.argmax(out)].item()

# 检测
def predict(frames):
    for i, frame in enumerate(frames):
        face = detect_crop_face_base_mtcnn(frame)
        face = transform(face).unsqueeze(dim=0)
        if i == 0:
            faces = face
        else:
            faces = torch.cat((faces, face), dim=0)

    faces = faces.to(torch.float32)

    return detect_engagement(faces.unsqueeze(dim=0))


if __name__ == '__main__':
    img = cv2.imread('frame30.jpg')
    frames = list()
    for i in range(8):
        frames.append(img)
    print(predict(frames))
