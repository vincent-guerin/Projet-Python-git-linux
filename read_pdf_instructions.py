import pypdf
import sys

try:
    reader = pypdf.PdfReader("Project (1).pdf")
    text = ""
    with open("instructions.txt", "w", encoding="utf-8") as f:
        for page in reader.pages:
            f.write(page.extract_text() + "\n")
    print("Successfully wrote instructions.txt")
except Exception as e:
    print(f"Error reading PDF: {e}")
