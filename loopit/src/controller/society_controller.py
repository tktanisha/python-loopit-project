from fastapi import status
from schemas.society import SocietyRequest,SocietyResponse
from service.society_service import SocietyService
from helpers.error_handler import write_error_response
from helpers.success_handler import write_success_response


async def create_society(society: SocietyRequest, society_service: SocietyService):

    try:
        await society_service.create_society(
            name=society.name,
            location=society.location,
            pincode=society.pincode,
        )
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="failed to create society",
            details=str(e),
        )

    return write_success_response(
        status_code=status.HTTP_201_CREATED,
        message="society created successfully",
    )


async def get_all_societies(society_service: SocietyService):
   
    try:
        societies = await society_service.get_all_societies()
        if societies and hasattr(societies[0], "model_dump"):
            societies = [s.model_dump() for s in societies]
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="failed to fetch societies",
            details=str(e),
        )

    return write_success_response(
        status_code=status.HTTP_200_OK,
        data=societies,
    )


async def update_society(id: int, society: SocietyRequest, society_service: SocietyService):

    try:
        await society_service.update_society(
            id=id,
            name=society.name,
            location=society.location,
            pincode=society.pincode,
        )
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="failed to update society",
            details=str(e),
        )

    return write_success_response(
        status_code=status.HTTP_205_RESET_CONTENT,
        message="society updated successfully",
    )


async def delete_society(id: int, society_service: SocietyService):

    try:
        await society_service.delete_society(id)
    except Exception as e:
        return write_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="failed to delete society",
            details=str(e),
        )

    return write_success_response(
        status_code=status.HTTP_200_OK,
        message="society deleted successfully",
    )
