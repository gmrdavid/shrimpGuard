import zipfile
import xml.etree.ElementTree as ET

def read_docx(path):
    with zipfile.ZipFile(path, 'r') as z:
        xml_content = z.read('word/document.xml')
    tree = ET.fromstring(xml_content)
    # Extract text from all <w:t> elements
    paragraphs = []
    for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = [node.text for node in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
        if texts:
            paragraphs.append("".join(texts))
    return "\n".join(paragraphs)

text1 = read_docx(r"c:\Users\gliam\Documents\References\1st Sem A.Y. 2026 - 2027\Capstone 2\Sub-parts of the Technicality of the Project.docx")
print("=== Sub-parts of the Technicality of the Project ===")
print(text1[:2000])

text2 = read_docx(r"c:\Users\gliam\Documents\References\1st Sem A.Y. 2026 - 2027\Capstone 2\CAPSTONE 2 Manuscript Format.docx")
print("\n=== CAPSTONE 2 Manuscript Format ===")
# Search for Chapter 3 or Methodology
lines = text2.split('\n')
for i, l in enumerate(lines):
    if any(k in l.lower() for k in ['chapter 3', 'methodology', 'research design', 'development methodology']):
        print(f"Line {i}: {l}")
        for j in range(max(0, i-5), min(len(lines), i+30)):
            print(f"  {lines[j]}")
        break
