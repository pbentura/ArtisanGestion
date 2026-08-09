from reportlab.platypus import SimpleDocTemplate, Image
import urllib.request
import io
doc = SimpleDocTemplate("test_img.pdf")
# A 1x1 black pixel in base64
b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
from urllib.request import urlopen
req = urlopen(b64)
img_data = req.read()
img = Image(io.BytesIO(img_data), width=50, height=50)
doc.build([img])
print("Success")
