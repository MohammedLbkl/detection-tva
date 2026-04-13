import re


def html_to_text(content):
    text = content
    # Retours à la ligne pour les balises block
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</h[1-6]>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</tr>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</td>', '\t', text, flags=re.IGNORECASE)
    text = re.sub(r'</th>', '\t', text, flags=re.IGNORECASE)
    # Supprimer toutes les balises HTML restantes
    text = re.sub(r'<[^>]+>', '', text)
    # Décoder les entités HTML courantes
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    # Lignes vides multiples
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Espaces en fin de ligne
    text = re.sub(r'[ \t]+\n', '\n', text)
    return text.strip()
