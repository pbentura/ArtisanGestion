from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate
styles = getSampleStyleSheet()
style = styles["Normal"]
doc = SimpleDocTemplate("test.pdf")
elements = []
elements.append(Paragraph("<h3>Test Heading</h3> <p>This is a <strong>test</strong> with some <span style='color:blue;'>blue</span> text.</p>", style))
doc.build(elements)
