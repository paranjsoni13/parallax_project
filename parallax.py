import cv2
import numpy as np
import imageio
import torch
from torchvision.transforms import Compose, ToTensor, Resize
from PIL import Image

# Initialize the MiDaS model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
midas = torch.hub.load("intel-isl/MiDaS", "MiDaS").to(device).eval()
midas_transforms = Compose([
    Resize(384),
    ToTensor(),
    lambda x: x.to(device),
])

def get_depth_map(img):
    # Resize the image for MiDaS model compatibility
    target_size = (384, 384)
    img_resized = img.resize(target_size, Image.Resampling.LANCZOS)

    # Apply transformations and predict
    input_batch = midas_transforms(img_resized).unsqueeze(0)
    with torch.no_grad():
        prediction = midas(input_batch)
    depth_map = prediction.squeeze().cpu().numpy()
    depth_map = cv2.resize(depth_map, (img.width, img.height))
    return depth_map

def create_parallax(image_path, num_frames=15, parallax_intensity=7):
    # Load and convert the image from BGR to RGB
    input_image = cv2.imread(image_path)
    if input_image is None:
        raise ValueError("Image not found or path is incorrect")
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)

    # Generate and normalize the depth map
    img = Image.open(image_path)
    depth_map = get_depth_map(img)
    depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())

    # Create an output image list with the parallax effect
    output_images = []
    for frame in range(num_frames):
        shifted_image = np.zeros_like(input_image)
        displacement = (frame - num_frames / 2) * parallax_intensity
        for y in range(input_image.shape[0]):
            for x in range(input_image.shape[1]):
                depth = depth_map[y, x]
                shift = int(displacement * depth)
                new_x = x + shift
                new_x = max(0, min(input_image.shape[1] - 1, new_x))
                shifted_image[y, x] = input_image[y, new_x]
        output_images.append(shifted_image)

    # Save the frames as a GIF
    output_file = f"static/uploads/output_parallax_{num_frames}.gif"
    imageio.mimsave(output_file, output_images, fps=7, loop=0)
    return output_file
