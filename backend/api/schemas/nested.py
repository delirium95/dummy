from api.schemas.posts import PostResponse
from api.schemas.users import UserResponse


class UserWithPostsResponse(UserResponse):
    posts: list[PostResponse]


class PostWithAuthorResponse(PostResponse):
    author: UserResponse
