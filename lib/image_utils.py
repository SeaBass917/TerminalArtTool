"""For all the image processing used in this project."""
from io import StringIO
import os
import cv2
import numpy as np

from lib.terminal_art import get_dot


def load_image(image_path: str) -> np.ndarray:
    if not os.path.exists(image_path):
        raise RuntimeError(f"Cannot access {image_path}")
    return cv2.imread(image_path)


def convert_to_edges(image: np.ndarray,
                     blur_kernel=(5, 5), threshold1=50, threshold2=150) -> np.ndarray:

    # 2. Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 3. Apply Gaussian blur to reduce noise (optional but recommended)
    # The kernel size (5,5) and standard deviations (0,0) are common choices.
    blurred_image = cv2.GaussianBlur(gray_image, blur_kernel, 0)

    # 4. Apply Canny edge detection
    # Adjust threshold1 and threshold2 for desired edge sensitivity
    edges = cv2.Canny(blurred_image, threshold1=threshold1,
                      threshold2=threshold2)

    return edges


def downscale(window: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Downscales edge data using mean-pooling.

    Args:
        window (np.ndarray): The input window of edge data.
        shape (tuple[int, int]): The desired output shape (rows, columns).

    Returns:
        np.ndarray: The downscaled edge data.
    """
    input_rows, input_cols = window.shape
    output_rows, output_cols = shape

    # Calculate the block sizes for mean-pooling
    block_rows = input_rows // output_rows
    block_cols = input_cols // output_cols

    # Trim the window from the right and bottom to fit the downscaled shape.
    trimmed_rows = block_rows * output_rows
    trimmed_cols = block_cols * output_cols
    trimmed_window = window[:trimmed_rows, :trimmed_cols]

    # Reshape the array to a grid of blocks and then average each block
    downscaled = trimmed_window.reshape(
        output_rows, block_rows, output_cols, block_cols)
    downscaled = downscaled.mean(axis=3)  # Average over the block columns
    downscaled = downscaled.mean(axis=1)  # Average over the block rows

    return (0.5 <= downscaled) * 255


def high_contrast_overlay(edges: np.ndarray, image: np.ndarray, threshold=50) -> np.ndarray:
    """Find particularly dark parts of the image and add them to the edge map.

    Args:
        edges (np.ndarray): The existing edge map, a 2D NumPy array with values 0 or 255.
        image (np.ndarray): The original input image, an RGB 3D NumPy array.
        threshold (int): The luminance threshold to identify dark areas.

    Returns:
        np.ndarray: The combined mask, a 2D NumPy array with values 0 or 255.
    """
    # 1. Check for compatibility and handle potential errors
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Input 'image' must be a 3-channel RGB array.")
    if edges.ndim != 2:
        raise ValueError("Input 'edges' must be a 2D array.")
    if image.shape[:2] != edges.shape:
        raise ValueError(
            "Image and edges must have the same height and width.")

    # 2. Convert the image to grayscale to find luminance
    # The standard formula for luminance is 0.299*R + 0.587*G + 0.114*B
    luminance = np.dot(image[..., :3], [0.299, 0.587, 0.114])

    # 3. Create a boolean mask for low luminance areas
    # The condition `luminance < threshold` will result in a boolean array
    # with True for pixels below the threshold and False otherwise.
    low_luminance_mask = luminance < threshold

    # 4. Combine the masks using a logical OR operation
    # First, convert the integer edge map to a boolean mask.
    edges_mask = edges > 0  # True for edge pixels (255), False otherwise (0)

    # Use np.logical_or to combine the two boolean masks
    combined_mask = np.logical_or(edges_mask, low_luminance_mask)

    # Convert the resulting boolean mask back to a 0/255 integer array
    # The astype(np.uint8) ensures the result is in the correct format.
    result = combined_mask.astype(np.uint8) * 255

    return result


def convert_to_terminal_art(image: np.ndarray, num_dots=4, scale: float | None = None, invert_color=True) -> str:
    """Take an edge matrix and return art."""
    window_rows = num_dots
    window_cols = 2

    if num_dots == 3:
        raise NotImplementedError("Sorry, no 3x2 yet")
    if num_dots != 4:
        raise RuntimeError("Must be 3 or 4 dots.")
    if scale is not None and (scale <= 0 or 1 < scale):
        raise RuntimeError(f"Invalid scale {scale}! Must be between (0,1]")

    # Use a stream to process all the 100-1000's of chars
    # Maybe overkill
    str_out = StringIO()

    # Simple case: Output the same size of the image.
    if scale is None:
        img_height, img_width = image.shape[:2]
    else:
        img_height, img_width = image.shape[:2]
        output_shape = int(img_height * scale), int(img_width * scale)
        image = downscale(image, shape=output_shape)
        img_height, img_width = image.shape[:2]

    for r in range(0, img_height - window_rows + 1, window_rows):
        for c in range(0, img_width - window_cols + 1, window_cols):
            window = image[r:r + window_rows, c:c + window_cols]
            c = get_dot(window, invert=invert_color)
            str_out.write(c)
        str_out.write("\n")

    # Convert back to string and return
    str_out.seek(0)
    return str_out.read()
