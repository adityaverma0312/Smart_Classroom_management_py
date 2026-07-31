import os
from datetime import datetime

# Safe import of cv2 and face_recognition
try:
    import cv2
    import face_recognition
    CV2_AVAILABLE = True
except Exception:
    CV2_AVAILABLE = False
    cv2 = None
    face_recognition = None

import numpy as np
import pandas as pd

from utils.constants import KNOWN_FACES_DIR

def get_student_image(student_name):
    if not CV2_AVAILABLE:
        return None

    for ext in [".jpg", ".jpeg", ".png"]:
        path = os.path.join(KNOWN_FACES_DIR, f"{student_name}{ext}")
        if os.path.exists(path):
            return path
    return None