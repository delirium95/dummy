export type SortDirection = 'asc' | 'desc';

export interface PageResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface User {
  id: number;
  external_id: number | null;
  first_name: string;
  last_name: string;
  email: string;
  username: string;
  created_at: string;
  updated_at: string;
}

export interface CreateUserRequest {
  first_name: string;
  last_name: string;
  email: string;
  username: string;
}

export interface UpdateUserRequest {
  first_name?: string;
  last_name?: string;
  email?: string;
  username?: string;
}

export interface Post {
  id: number;
  external_id: number | null;
  user_id: number;
  title: string;
  body: string;
  tags: string[];
  reactions_likes: number;
  reactions_dislikes: number;
  views: number;
  created_at: string;
  updated_at: string;
}

export interface UserWithPosts extends User {
  posts: Post[];
}

export interface PostWithAuthor extends Post {
  author: User;
}

export interface CreatePostRequest {
  user_id: number;
  title: string;
  body: string;
  tags: string[];
}

export interface UpdatePostRequest {
  title?: string;
  body?: string;
  tags?: string[];
}

export interface ApiErrorShape {
  status: number;
  code: string;
  detail: string;
}

export interface SyncResult {
  users_added: number;
  users_updated: number;
  posts_added: number;
  posts_updated: number;
  posts_skipped_missing_author: number;
}

export interface ProblemDetail {
  code: string;
  detail: string;
}
