import os
import numpy as np
import cv2
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
from django.conf import settings

# 1. Helper Functions

def read_and_preprocess(image_file_path, size=(180, 200)):
    # Open the image file using OpenCV
    # file = settings.BASE_DIR / image_file_path
    print(image_file_path)
    image = cv2.imread(image_file_path, cv2.IMREAD_GRAYSCALE)
    img_resized = cv2.resize(image, size)
    return img_resized.flatten()

def construct_data_matrix(image_file_paths, size=(180, 200)):
    data = []
    image_files = [f for f in os.listdir(image_file_paths) if os.path.isfile(os.path.join(image_file_paths, f))]
    for image_file_path in image_files:
        path = image_file_paths + '/' + image_file_path
        data.append(read_and_preprocess(path, size))
    return np.array(data).T

def mean_centering(matrix):
    mean_face = np.mean(matrix, axis=1).reshape(-1, 1)
    return matrix - mean_face, mean_face

def compute_eigenfaces(matrix, num_eigenfaces=None):
    U, S, Vt = np.linalg.svd(matrix, full_matrices=False)
    if num_eigenfaces:
        U = U[:, :num_eigenfaces]
    return U

def recognize_face(new_face, projected_faces, eigenfaces, mean_face, threshold=2200):
    new_face_centered = new_face - mean_face.ravel()
    new_face_projected = np.dot(eigenfaces.T, new_face_centered).reshape(-1, 1)
    distances = np.linalg.norm(projected_faces - new_face_projected, axis=0)
    
    min_distance = np.min(distances)
    
    if min_distance < threshold:
        return np.argmin(distances)
    else:
        return -1  # indicating face not recognized

def train(image_file_paths):
    A = construct_data_matrix(image_file_paths)
    A_centered, mean_face = mean_centering(A)
    eigenfaces = compute_eigenfaces(A_centered, num_eigenfaces=20)
    projected_faces = np.dot(eigenfaces.T, A_centered)
    
    return {
        'eigenfaces': eigenfaces,
        'mean_face': mean_face,
        'projected_faces': projected_faces
    }

def test_face_recognitions(test_image_file_paths, train_image_file_paths, model):
    for test_image_file_path in test_image_file_paths:
        new_face = read_and_preprocess(test_image_file_path)
        recognized_index = recognize_face(new_face, model['projected_faces'], model['eigenfaces'], model['mean_face'])

        if recognized_index == -1:
            continue

        recognized_image_file_path = train_image_file_paths[recognized_index]

        # You can handle the recognized image file path as needed.

        return recognized_image_file_path
