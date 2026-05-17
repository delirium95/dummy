import { useState } from 'react';
import {
  errorMessage,
  useCreatePostMutation,
  useDeletePostMutation,
  useGetUserPostsQuery,
  useUpdatePostMutation,
} from '../services/api';
import type { CreatePostRequest, Post, User } from '../types/domain';
import { Modal } from './Modal';
import { PostForm } from './PostForm';

interface Props {
  user: User;
  onClose: () => void;
}

const PAGE_SIZE = 50;

export function UserPostsModal({ user, onClose }: Props): JSX.Element {
  const { data, isLoading, isFetching, error } = useGetUserPostsQuery({
    id: user.id,
    limit: PAGE_SIZE,
    offset: 0,
    sort: 'id',
    direction: 'asc',
  });

  const [createPost] = useCreatePostMutation();
  const [updatePost] = useUpdatePostMutation();
  const [deletePost, { isLoading: deleting }] = useDeletePostMutation();

  const [formOpen, setFormOpen] = useState<boolean>(false);
  const [editing, setEditing] = useState<Post | null>(null);

  async function handleCreate(body: CreatePostRequest): Promise<void> {
    await createPost(body).unwrap();
    setFormOpen(false);
  }

  async function handleUpdate(body: CreatePostRequest): Promise<void> {
    if (editing === null) return;
    const { user_id: _userId, ...changes } = body;
    await updatePost({ id: editing.id, userId: user.id, body: changes }).unwrap();
    setEditing(null);
  }

  async function handleDelete(post: Post): Promise<void> {
    if (!window.confirm(`Delete post #${post.id}?`)) return;
    try {
      await deletePost({ id: post.id, userId: user.id }).unwrap();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to delete';
      window.alert(message);
    }
  }

  const posts = data?.items ?? [];

  return (
    <>
      <Modal open onClose={onClose}>
        <div className="posts-modal">
          <header className="posts-modal-header">
            <h2>
              Posts of {user.first_name} {user.last_name} <small>@{user.username}</small>
            </h2>
            <div className="actions">
              <button type="button" onClick={() => setFormOpen(true)}>
                New post
              </button>
              <button type="button" onClick={onClose}>
                Close
              </button>
            </div>
          </header>

          {error && (
            <div className="banner error" role="alert">
              {errorMessage(error)}
            </div>
          )}

          {isLoading ? (
            <div className="state">Loading…</div>
          ) : posts.length === 0 ? (
            <div className="state">No posts yet.</div>
          ) : (
            <ul className="posts-list">
              {posts.map((p) => (
                <li key={p.id} className="post-item">
                  <div className="post-meta">
                    <strong>#{p.id}</strong> · {p.title}
                  </div>
                  <p className="post-body">{p.body}</p>
                  {p.tags.length > 0 && (
                    <div className="post-tags">
                      {p.tags.map((t) => (
                        <span key={t} className="tag">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                  <div className="actions">
                    <button type="button" onClick={() => setEditing(p)}>
                      Edit
                    </button>
                    <button
                      type="button"
                      className="danger"
                      onClick={() => void handleDelete(p)}
                      disabled={deleting}
                    >
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}

          {isFetching && !isLoading && <div className="state subtle">Refreshing…</div>}
          {data && data.total > posts.length && (
            <div className="state subtle">
              Showing {posts.length} of {data.total} (newest first via /users/{user.id}/posts)
            </div>
          )}
        </div>
      </Modal>

      <Modal open={formOpen} onClose={() => setFormOpen(false)}>
        {formOpen && (
          <PostForm userId={user.id} onSubmit={handleCreate} onCancel={() => setFormOpen(false)} />
        )}
      </Modal>

      <Modal open={editing !== null} onClose={() => setEditing(null)}>
        {editing && (
          <PostForm
            userId={user.id}
            post={editing}
            onSubmit={handleUpdate}
            onCancel={() => setEditing(null)}
          />
        )}
      </Modal>
    </>
  );
}
