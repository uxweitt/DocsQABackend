from pypdf import PdfReader
from langchain_core.documents import Document

def exctract_from_pdf(path: str) -> list[Document]:
    texts = list()
    with open(path, 'rb') as pdf_file:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            texts.append(
                Document(
                    page_content=page.extract_text(),
                    metadata={},
                )
            )
    return texts
    
def exctract_from_md(path: str) -> Document:
    text = ""
    with open(path, 'r') as md_file:
        text = md_file.read()
    if not text:
        raise ValueError("PDF has no extracteble text")
    return Document(
        page_content=text,
        metadata={},
    )