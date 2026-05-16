from domain.ids import ExternalPostID, ExternalUserID, PostID, UserID
from domain.post.model import PostModel
from domain.post.value_objects import Body, Tags, Title
from domain.user.model import UserModel
from domain.user.value_objects import Email, FullName, Username
from infrastructure.database.models import PostRow, UserRow


def user_row_to_model(row: UserRow) -> UserModel:
    return UserModel(
        id=UserID(row.id),
        external_id=ExternalUserID(row.external_id) if row.external_id is not None else None,
        name=FullName(first=row.first_name, last=row.last_name),
        email=Email(value=row.email),
        username=Username(value=row.username),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def post_row_to_model(row: PostRow) -> PostModel:
    return PostModel(
        id=PostID(row.id),
        external_id=ExternalPostID(row.external_id) if row.external_id is not None else None,
        user_id=UserID(row.user_id),
        title=Title(value=row.title),
        body=Body(value=row.body),
        tags=Tags(values=tuple(row.tags)),
        reactions_likes=row.reactions_likes,
        reactions_dislikes=row.reactions_dislikes,
        views=row.views,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
