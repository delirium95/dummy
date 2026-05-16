from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from api.schemas.sync import SyncResultResponse
from containers import Container
from domain.sync.interfaces import SyncDataUseCase

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("", response_model=SyncResultResponse, status_code=status.HTTP_200_OK)
@inject
async def run_sync(
    use_case: SyncDataUseCase = Depends(Provide[Container.sync_data_use_case]),
) -> SyncResultResponse:
    result = await use_case()
    return SyncResultResponse.from_domain(result)
