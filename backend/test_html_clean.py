import re

def clean_html_for_reportlab(html_text: str) -> str:
    if not html_text:
        return ""
    text = str(html_text)
    
    # Remplacer les div et p par des br
    text = text.replace('</div>', '<br/>')
    text = text.replace('</p>', '<br/>')
    text = re.sub(r'<div[^>]*>', '', text)
    text = re.sub(r'<p[^>]*>', '', text)
    
    # Titres h1-h6 en gras et bleu
    text = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'<br/><font color="#2563eb"><b>\1</b></font><br/>', text, flags=re.IGNORECASE)
    
    # Listes
    text = text.replace('<ul>', '')
    text = text.replace('</ul>', '<br/>')
    text = text.replace('<ol>', '')
    text = text.replace('</ol>', '<br/>')
    text = re.sub(r'<li[^>]*>', '• ', text)
    text = text.replace('</li>', '<br/>')
    
    # Strong / b
    text = re.sub(r'<strong[^>]*>', '<b>', text)
    text = text.replace('</strong>', '</b>')
    
    # Nettoyer attributs span et autres balises non supportées
    # ReportLab supporte <b>, <i>, <u>, strike, super, sub, font, a. 
    # On va juste supprimer les <span>, <img>, etc.
    text = re.sub(r'<span[^>]*>', '', text)
    text = text.replace('</span>', '')
    text = re.sub(r'<img[^>]*>', '', text)
    
    # Retirer tous les attributs des balises pour éviter les crash, SAUF pour <font>
    # C'est compliqué avec des regex, on va plutôt laisser les <b>, <i>, <u>
    
    # Nettoyer les sauts de ligne multiples
    text = re.sub(r'(<br\s*/?>\s*){3,}', '<br/><br/>', text)
    text = re.sub(r'^(<br\s*/?>\s*)+', '', text)
    
    return text.strip()

print(repr(clean_html_for_reportlab("<h3>Test</h3><p>Texte avec <strong>gras</strong> et <span style='color:red'>span</span>.</p>")))
