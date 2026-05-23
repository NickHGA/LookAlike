import cv2

def cartoonify_image(image_path: str, output_path: str):
    """
    Apply a cartoon effect to an image using OpenCV filters.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Impossible de lire l'image: {image_path}")
    
    # 1. Edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    
    # 2. Color smoothing (Bilateral Filter preserves edges while smoothing color)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    
    # 3. Combine
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    
    # Save output
    cv2.imwrite(output_path, cartoon)
    return output_path
