import os
import torch
import numpy as np
import cv2
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1

# --------------------- Configuration ---------------------
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Face detector and FaceNet model
mtcnn = MTCNN(image_size=160, margin=20, min_face_size=40, device=device)
model = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Dataset and output folders
base_dataset_path = 'dataset'
students_path = os.path.join(base_dataset_path, 'students')
teachers_path = os.path.join(base_dataset_path, 'teachers')

embeddings_dir = 'embeddings'
os.makedirs(embeddings_dir, exist_ok=True)

# ---------------------------------------------------------

def generate_embeddings(source_dir: str) -> dict:
    """
    Generate embeddings for all subfolders inside source_dir.
    Each subfolder name format: ID_Name
    """
    embedding_dict = {}
    print(f"🔍 Generating embeddings from: {source_dir}")

    for folder_name in os.listdir(source_dir):
        person_folder = os.path.join(source_dir, folder_name)
        if not os.path.isdir(person_folder):
            continue

        # Extract ID and Name (split only once)
        parts = folder_name.split("_", 1)
        if len(parts) == 2:
            person_id, person_name = parts
        else:
            person_id, person_name = parts[0], "Unknown"

        person_name = person_name.replace(" ", "_")
        embeddings = []

        for image_name in os.listdir(person_folder):
            image_path = os.path.join(person_folder, image_name)

            img_bgr = cv2.imread(image_path)
            if img_bgr is None:
                continue

            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)

            # Detect and encode face
            face_tensor = mtcnn(img_pil)
            if face_tensor is not None:
                face_tensor = face_tensor.unsqueeze(0).to(device)
                with torch.no_grad():
                    embedding = model(face_tensor).cpu().numpy()
                    embeddings.append(embedding)

        if embeddings:
            avg_embedding = np.mean(embeddings, axis=0)
            embedding_dict[folder_name] = {
                "id": person_id,
                "name": person_name,
                "embedding": avg_embedding
            }
            print(f"✅ Processed: {person_name} (ID: {person_id}, {len(embeddings)} images)")

    return embedding_dict

# ------------------ Generate & Save -----------------------
# Students
student_embeddings = generate_embeddings(students_path)
np.save(os.path.join(embeddings_dir, 'student_embeddings.npy'), student_embeddings)
print("💾 Saved student embeddings to embeddings/student_embeddings.npy")

# Teachers
teacher_embeddings = generate_embeddings(teachers_path)
np.save(os.path.join(embeddings_dir, 'teacher_embeddings.npy'), teacher_embeddings)
print("💾 Saved teacher embeddings to embeddings/teacher_embeddings.npy")
