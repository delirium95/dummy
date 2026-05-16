from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from api.schemas.pagination import PageResponse, PaginationParams, pagination_params
from api.schemas.posts import CreatePostRequest, PostResponse, UpdatePostRequest
from api.schemas.users import UserResponse
from containers import Container
from domain.ids import PostID
from domain.post.interfaces import (
    CreatePostUseCase,
    DeletePostUseCase,
    GetPostUseCase,
    ListPostsUseCase,
    PostRepository,
    UpdatePostUseCase,
)
from domain.user.interfaces import GetUserUseCase

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PageResponse[PostResponse])
@inject
async def list_posts(
    params: PaginationParams = Depends(pagination_params),
    use_case: ListPostsUseCase = Depends(Provide[Container.list_posts_use_case]),
) -> PageResponse[PostResponse]:
    page_request = params.to_page_request(allowed_fields=PostRepository.SORTABLE_FIELDS)
    page = await use_case(page_request)
    return PageResponse[PostResponse](
        items=[PostResponse.from_domain(p) for p in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/{post_id}", response_model=PostResponse)
@inject
async def get_post(
    post_id: int,
    use_case: GetPostUseCase = Depends(Provide[Container.get_post_use_case]),
) -> PostResponse:
    post = await use_case(PostID(post_id))
    return PostResponse.from_domain(post)


@router.get("/{post_id}/author", response_model=UserResponse)
@inject
async def get_post_author(
    post_id: int,
    get_post: GetPostUseCase = Depends(Provide[Container.get_post_use_case]),
    get_user: GetUserUseCase = Depends(Provide[Container.get_user_use_case]),
) -> UserResponse:
    post = await get_post(PostID(post_id))
    author = await get_user(post.user_id)
    return UserResponse.from_domain(author)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_post(
    body: CreatePostRequest,
    use_case: CreatePostUseCase = Depends(Provide[Container.create_post_use_case]),
) -> PostResponse:
    post = await use_case(body.to_domain())
    return PostResponse.from_domain(post)


@router.put("/{post_id}", response_model=PostResponse)
@inject
async def update_post(
    post_id: int,
    body: UpdatePostRequest,
    use_case: UpdatePostUseCase = Depends(Provide[Container.update_post_use_case]),
) -> PostResponse:
    post = await use_case(
        PostID(post_id),
        title=body.title_or_none(),
        body=body.body_or_none(),
        tags=body.tags_or_none(),
    )
    return PostResponse.from_domain(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_post(
    post_id: int,
    use_case: DeletePostUseCase = Depends(Provide[Container.delete_post_use_case]),
) -> None:
    await use_case(PostID(post_id))
