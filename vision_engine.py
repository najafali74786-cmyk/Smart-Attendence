import cv2
import numpy as np
import face_recognition
import base64

def get_face_encoding_from_base64(base64_string):
    """
    Yeh function LED screen se aane wali photo ko decode karta hai
    aur chehre ke 128 mathematical points nikaalta hai.
    """
    try:
        # 1. Hatao faltu header agar HTML canvas se aaya hai
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        
        # 2. Text (Base64) ko wapas image ke bytes mein badlo
        img_data = base64.b64decode(base64_string)
        
        # 3. OpenCV ke samajhne layaq Numpy array banao
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 4. OpenCV (BGR) ko Face_Recognition (RGB) colors mein badlo
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 5. Chehre dhoondo aur unka map (encoding) banao
        face_locations = face_recognition.face_locations(rgb_img)
        encodings = face_recognition.face_encodings(rgb_img, face_locations)
        
        # Checks: Agar chehra na ho, ya 1 se zyada hon toh error do
        if len(encodings) == 0:
            return None, "No face found in the image. Please look at the camera."
        elif len(encodings) > 1:
            return None, "Multiple faces found. Only one person should stand in front."
        
        # Agar sab theek hai, toh pehle chehre ka map (List format mein) wapas bhej do
        return encodings[0].tolist(), "Success"
        
    except Exception as e:
        return None, f"Error processing image: {str(e)}"
    
    # Yeh function database ke sab chehron ko live chehre se match karega
def match_face(unknown_encoding, known_encodings_list):
    try:
        # Known encodings ko numpy arrays mein badlo
        known_encodings_np = [np.array(enc) for enc in known_encodings_list]
        unknown_encoding_np = np.array(unknown_encoding)
        
        # Match karo (Tolerance 0.5 rakhi hai taake strict checking ho, fake match na ho)
        matches = face_recognition.compare_faces(known_encodings_np, unknown_encoding_np, tolerance=0.5)
        face_distances = face_recognition.face_distance(known_encodings_np, unknown_encoding_np)
        
        if len(face_distances) == 0:
            return -1 # Koi record nahi
            
        # Sab se zyada milta julta chehra dhoondo
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            return best_match_index # Match mil gaya!
            
        return -1 # Match nahi mila (Unregistered face)
    except Exception as e:
        print(f"Matcher Error: {e}")
        return -1