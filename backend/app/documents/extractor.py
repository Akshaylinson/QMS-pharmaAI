from io import BytesIO
from email import policy
from email.parser import BytesParser
def extract_document(filename: str, content: bytes) -> str:
    suffix=filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
    if suffix == 'txt': return content.decode('utf-8', errors='replace')
    if suffix == 'pdf':
        import fitz
        with fitz.open(stream=content, filetype='pdf') as doc: return '\n'.join(page.get_text() for page in doc)
    if suffix == 'docx':
        from docx import Document
        return '\n'.join(p.text for p in Document(BytesIO(content)).paragraphs)
    if suffix == 'eml':
        message=BytesParser(policy=policy.default).parsebytes(content)
        body=message.get_body(preferencelist=('plain',)); return body.get_content() if body else str(message)
    raise ValueError('Supported formats are PDF, DOCX, TXT, and EML.')
