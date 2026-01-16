import easyocr

# Load once (GPU auto-detect)
reader = easyocr.Reader(['en'], gpu=False)

def read_plate_easy(img):
    results = reader.readtext(img)
    if not results:
        return "NOT_DETECTED"

    # take highest confidence text
    results = sorted(results, key=lambda x: x[2], reverse=True)
    return results[0][1].replace(" ", "")
