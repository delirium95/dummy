import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query/react';
import type { SerializedError } from '@reduxjs/toolkit';
import type {
  ApiErrorShape,
  CreatePostRequest,
  CreateUserRequest,
  PageResponse,
  Post,
  PostWithAuthor,
  SortDirection,
  SyncResult,
  UpdatePostRequest,
  UpdateUserRequest,
  User,
  UserWithPosts,
} from '@/types/domain';

const BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim() || 'http://localhost:8000';

export interface ListQuery {
  limit: number;
  offset: number;
  sort: string;
  direction: SortDirection;
}

export function errorMessage(err: ApiErrorShape | SerializedError | undefined): string {
  if (!err) return '';
  if ('detail' in err) return err.detail;
  return err.message ?? 'Unknown error';
}

function toApiError(error: FetchBaseQueryError): ApiErrorShape {
  if (error.status === 'FETCH_ERROR' || error.status === 'TIMEOUT_ERROR') {
    return { status: 0, code: 'network_error', detail: error.error };
  }
  if (error.status === 'PARSING_ERROR' || error.status === 'CUSTOM_ERROR') {
    return { status: 0, code: 'parsing_error', detail: error.error ?? 'Parsing error' };
  }
  const status = error.status;
  const body = error.data as { code?: string; detail?: string } | string | null | undefined;
  let code = 'http_error';
  let detail = `${status}`;
  if (typeof body === 'object' && body !== null) {
    if (typeof body.code === 'string') code = body.code;
    if (typeof body.detail === 'string') detail = body.detail;
  } else if (typeof body === 'string' && body.length > 0) {
    detail = body;
  }
  return { status, code, detail };
}

const rawBaseQuery = fetchBaseQuery({
  baseUrl: BASE_URL,
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
});

const baseQuery: BaseQueryFn<string | FetchArgs, unknown, ApiErrorShape> = async (
  args,
  api,
  extra,
) => {
  const result = await rawBaseQuery(args, api, extra);
  if (result.error) {
    return { error: toApiError(result.error) };
  }
  return { data: result.data };
};

type TagType = 'User' | 'Post';

export const api = createApi({
  reducerPath: 'api',
  baseQuery,
  tagTypes: ['User', 'Post'] satisfies TagType[],
  endpoints: (build) => ({
    getUsers: build.query<PageResponse<User>, ListQuery>({
      query: (q) =>
        `/users?limit=${q.limit}&offset=${q.offset}&sort=${q.sort}&direction=${q.direction}`,
      providesTags: (result) =>
        result
          ? [
              ...result.items.map((u) => ({ type: 'User' as const, id: u.id })),
              { type: 'User' as const, id: 'LIST' },
            ]
          : [{ type: 'User' as const, id: 'LIST' }],
    }),
    getUser: build.query<UserWithPosts, number>({
      query: (id) => `/users/${id}`,
      providesTags: (result, _err, id) =>
        result
          ? [
              { type: 'User' as const, id },
              ...result.posts.map((p) => ({ type: 'Post' as const, id: p.id })),
            ]
          : [{ type: 'User' as const, id }],
    }),
    getUserPosts: build.query<PageResponse<Post>, { id: number } & ListQuery>({
      query: ({ id, limit, offset, sort, direction }) =>
        `/users/${id}/posts?limit=${limit}&offset=${offset}&sort=${sort}&direction=${direction}`,
      providesTags: (result, _err, arg) =>
        result
          ? [
              ...result.items.map((p) => ({ type: 'Post' as const, id: p.id })),
              { type: 'Post' as const, id: `USER-${arg.id}` },
            ]
          : [{ type: 'Post' as const, id: `USER-${arg.id}` }],
    }),
    createUser: build.mutation<User, CreateUserRequest>({
      query: (body) => ({ url: '/users', method: 'POST', body }),
      invalidatesTags: [{ type: 'User', id: 'LIST' }],
    }),
    updateUser: build.mutation<User, { id: number; body: UpdateUserRequest }>({
      query: ({ id, body }) => ({ url: `/users/${id}`, method: 'PUT', body }),
      invalidatesTags: (_res, _err, arg) => [
        { type: 'User', id: arg.id },
        { type: 'User', id: 'LIST' },
      ],
    }),
    deleteUser: build.mutation<void, number>({
      query: (id) => ({ url: `/users/${id}`, method: 'DELETE' }),
      invalidatesTags: (_res, _err, id) => [
        { type: 'User', id },
        { type: 'User', id: 'LIST' },
        { type: 'Post', id: `USER-${id}` },
      ],
    }),

    getPosts: build.query<PageResponse<Post>, ListQuery>({
      query: (q) =>
        `/posts?limit=${q.limit}&offset=${q.offset}&sort=${q.sort}&direction=${q.direction}`,
      providesTags: (result) =>
        result
          ? [
              ...result.items.map((p) => ({ type: 'Post' as const, id: p.id })),
              { type: 'Post' as const, id: 'LIST' },
            ]
          : [{ type: 'Post' as const, id: 'LIST' }],
    }),
    getPost: build.query<PostWithAuthor, number>({
      query: (id) => `/posts/${id}`,
      providesTags: (_res, _err, id) => [{ type: 'Post' as const, id }],
    }),
    createPost: build.mutation<Post, CreatePostRequest>({
      query: (body) => ({ url: '/posts', method: 'POST', body }),
      invalidatesTags: (_res, _err, arg) => [
        { type: 'Post', id: 'LIST' },
        { type: 'Post', id: `USER-${arg.user_id}` },
        { type: 'User', id: arg.user_id },
      ],
    }),
    updatePost: build.mutation<Post, { id: number; userId: number; body: UpdatePostRequest }>({
      query: ({ id, body }) => ({ url: `/posts/${id}`, method: 'PUT', body }),
      invalidatesTags: (_res, _err, arg) => [
        { type: 'Post', id: arg.id },
        { type: 'Post', id: 'LIST' },
        { type: 'Post', id: `USER-${arg.userId}` },
        { type: 'User', id: arg.userId },
      ],
    }),
    deletePost: build.mutation<void, { id: number; userId: number }>({
      query: ({ id }) => ({ url: `/posts/${id}`, method: 'DELETE' }),
      invalidatesTags: (_res, _err, arg) => [
        { type: 'Post', id: arg.id },
        { type: 'Post', id: 'LIST' },
        { type: 'Post', id: `USER-${arg.userId}` },
        { type: 'User', id: arg.userId },
      ],
    }),

    runSync: build.mutation<SyncResult, void>({
      query: () => ({ url: '/sync', method: 'POST', body: {} }),
      invalidatesTags: [
        { type: 'User', id: 'LIST' },
        { type: 'Post', id: 'LIST' },
      ],
    }),
  }),
});

export const {
  useGetUsersQuery,
  useGetUserQuery,
  useGetUserPostsQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useGetPostsQuery,
  useGetPostQuery,
  useCreatePostMutation,
  useUpdatePostMutation,
  useDeletePostMutation,
  useRunSyncMutation,
} = api;
