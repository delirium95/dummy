import { apiClient } from './client';
import type {
  CreateUserRequest,
  PageResponse,
  Post,
  SortDirection,
  UpdateUserRequest,
  User,
} from '../types/domain';

export interface ListUsersQuery {
  limit: number;
  offset: number;
  sort: string;
  direction: SortDirection;
}

function toQueryString(query: ListUsersQuery): string {
  const params = new URLSearchParams({
    limit: String(query.limit),
    offset: String(query.offset),
    sort: query.sort,
    direction: query.direction,
  });
  return `?${params.toString()}`;
}

export const usersApi = {
  list(query: ListUsersQuery): Promise<PageResponse<User>> {
    return apiClient.get<PageResponse<User>>(`/users${toQueryString(query)}`);
  },
  get(id: number): Promise<User> {
    return apiClient.get<User>(`/users/${id}`);
  },
  listPosts(id: number, query: ListUsersQuery): Promise<PageResponse<Post>> {
    return apiClient.get<PageResponse<Post>>(`/users/${id}/posts${toQueryString(query)}`);
  },
  create(body: CreateUserRequest): Promise<User> {
    return apiClient.post<User>('/users', body);
  },
  update(id: number, body: UpdateUserRequest): Promise<User> {
    return apiClient.put<User>(`/users/${id}`, body);
  },
  remove(id: number): Promise<void> {
    return apiClient.delete<void>(`/users/${id}`);
  },
};
