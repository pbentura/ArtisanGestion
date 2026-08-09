from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
styles = getSampleStyleSheet()
style = styles["Normal"]
try:
    p = Paragraph("<h3>Test</h3> <p>This is a <strong>test</strong>.</p>", style)
    print("Success")
except Exception as e:
    print("Error:", e)
