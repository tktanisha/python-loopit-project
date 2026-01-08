from pydantic import BaseModel

class UploadImageRequest(BaseModel):
    fileName: str
    fileType: str
    fileContent: str