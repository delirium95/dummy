from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from api.schemas.pagination import PageResponse, PaginationParams, pagination_params
from api.schemas.posts import PostResponse
from api.schemas.users import CreateUserRequest, UpdateUserRequest, UserResponse
from containers import Container
from domain.ids import UserID
from domain.post.interfaces import ListPostsUseCase
from domain.shared.pagination import PageRequest, SortDirection, SortSpec
from domain.user.interfaces import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
    UserRepository,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=PageResponse[UserResponse])
@inject
async def list_users(
    params: PaginationParams = Depends(pagination_params),
    use_case: ListUsersUseCase = Depends(Provide[Container.list_users_use_case]),
) -> PageResponse[UserResponse]:
    page_request: PageRequest = params.to_page_request(
        allowed_fields=UserRepository.SORTABLE_FIELDS
    )
    page = await use_case(page_request)
    return PageResponse[UserResponse](
        items=[UserResponse.from_domain(u) for u in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/{user_id}", response_model=UserResponse)
@inject
async def get_user(
    user_id: int,
    use_case: GetUserUseCase = Depends(Provide[Container.get_user_use_case]),
) -> UserResponse:
    user = await use_case(UserID(user_id))
    return UserResponse.from_domain(user)


@router.get("/{user_id}/posts", response_model=PageResponse[PostResponse])
@inject
async def list_user_posts(
    user_id: int,
    params: PaginationParams = Depends(pagination_params),
    use_case: ListPostsUseCase = Depends(Provide[Container.list_posts_use_case]),
) -> PageResponse[PostResponse]:
    page_request = PageRequest(
        limit=params.limit,
        offset=params.offset,
        sort=SortSpec(field=params.sort, direction=params.direction or SortDirection.ASC),
    )
    page = await use_case(page_request, UserID(user_id))
    return PageResponse[PostResponse](
        items=[PostResponse.from_domain(p) for p in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    body: CreateUserRequest,
    use_case: CreateUserUseCase = Depends(Provide[Container.create_user_use_case]),
) -> UserResponse:
    user = await use_case(body.to_domain())
    return UserResponse.from_domain(user)


@router.put("/{user_id}", response_model=UserResponse)
@inject
async def update_user(
    user_id: int,
    body: UpdateUserRequest,
    use_case: UpdateUserUseCase = Depends(Provide[Container.update_user_use_case]),
) -> UserResponse:
    user = await use_case(
        UserID(user_id),
        name=body.name_or_none(),
        email=body.email_or_none(),
        username=body.username_or_none(),
    )
    return UserResponse.from_domain(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user(
    user_id: int,
    use_case: DeleteUserUseCase = Depends(Provide[Container.delete_user_use_case]),
) -> None:
    await use_case(UserID(user_id))
