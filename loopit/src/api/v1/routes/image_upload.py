from fastapi import APIRouter, HTTPException, status
from schemas.product_image import UploadImageRequest
from service.image_service import upload_image_via_lambda

router = APIRouter( prefix= "/images",tags=["Images"])


@router.put("/upload",status_code=status.HTTP_200_OK)
def upload_image(req: UploadImageRequest):
    try:
        payload_dict = req.model_dump() 

        result = upload_image_via_lambda(payload= payload_dict)#unpac into  dict 
        return result  

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
