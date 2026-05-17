import { useState, type FormEvent } from 'react';
import type { CreatePostRequest, Post } from '@/types/domain';

interface Props {
  userId: number;
  post?: Post;
  onSubmit: (data: CreatePostRequest) => Promise<void>;
  onCancel: () => void;
}

interface FieldErrors {
  title?: string;
  body?: string;
}

function validate(values: CreatePostRequest): FieldErrors {
  const errors: FieldErrors = {};
  if (values.title.trim().length === 0) errors.title = 'Title is required';
  if (values.body.trim().length === 0) errors.body = 'Body is required';
  return errors;
}

function parseTags(raw: string): string[] {
  return raw
    .split(',')
    .map((t) => t.trim())
    .filter((t) => t.length > 0);
}

export function PostForm({ userId, post, onSubmit, onCancel }: Props): JSX.Element {
  const isEdit = post !== undefined;
  const [title, setTitle] = useState<string>(post?.title ?? '');
  const [body, setBody] = useState<string>(post?.body ?? '');
  const [tagsRaw, setTagsRaw] = useState<string>(post ? post.tags.join(', ') : '');
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [serverError, setServerError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault();
    const data: CreatePostRequest = {
      user_id: userId,
      title,
      body,
      tags: parseTags(tagsRaw),
    };
    const validation = validate(data);
    setErrors(validation);
    if (Object.keys(validation).length > 0) return;
    setSubmitting(true);
    setServerError(null);
    try {
      await onSubmit(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to save';
      setServerError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="user-form" noValidate>
      <h2>{isEdit ? `Edit post #${post.id}` : 'New post'}</h2>

      <label>
        Title
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={submitting}
        />
        {errors.title && <span className="error">{errors.title}</span>}
      </label>

      <label>
        Body
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          disabled={submitting}
          rows={5}
        />
        {errors.body && <span className="error">{errors.body}</span>}
      </label>

      <label>
        Tags <small>(comma-separated)</small>
        <input
          type="text"
          value={tagsRaw}
          onChange={(e) => setTagsRaw(e.target.value)}
          disabled={submitting}
        />
      </label>

      {serverError && <div className="error server-error">{serverError}</div>}

      <div className="actions">
        <button type="submit" disabled={submitting}>
          {submitting ? 'Saving…' : isEdit ? 'Save' : 'Create'}
        </button>
        <button type="button" onClick={onCancel} disabled={submitting}>
          Cancel
        </button>
      </div>
    </form>
  );
}
