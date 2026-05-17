import { useState, type FormEvent } from 'react';
import type { CreateUserRequest, User } from '../types/domain';

interface Props {
  user?: User;
  onSubmit: (data: CreateUserRequest) => Promise<void>;
  onCancel: () => void;
}

interface FieldErrors {
  first_name?: string;
  last_name?: string;
  email?: string;
  username?: string;
}

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

function validate(values: CreateUserRequest): FieldErrors {
  const errors: FieldErrors = {};
  if (values.first_name.trim().length === 0) errors.first_name = 'First name is required';
  if (values.last_name.trim().length === 0) errors.last_name = 'Last name is required';
  if (!EMAIL_RE.test(values.email)) errors.email = 'Invalid email';
  if (values.username.trim().length === 0) errors.username = 'Username is required';
  return errors;
}

export function UserForm({ user, onSubmit, onCancel }: Props): JSX.Element {
  const isEdit = user !== undefined;
  const [firstName, setFirstName] = useState<string>(user?.first_name ?? '');
  const [lastName, setLastName] = useState<string>(user?.last_name ?? '');
  const [email, setEmail] = useState<string>(user?.email ?? '');
  const [username, setUsername] = useState<string>(user?.username ?? '');
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [serverError, setServerError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault();
    const data: CreateUserRequest = {
      first_name: firstName,
      last_name: lastName,
      email,
      username,
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
      <h2>{isEdit ? `Edit user #${user.id}` : 'Create user'}</h2>

      <label>
        First name
        <input
          type="text"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          disabled={submitting}
        />
        {errors.first_name && <span className="error">{errors.first_name}</span>}
      </label>

      <label>
        Last name
        <input
          type="text"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          disabled={submitting}
        />
        {errors.last_name && <span className="error">{errors.last_name}</span>}
      </label>

      <label>
        Email
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={submitting}
        />
        {errors.email && <span className="error">{errors.email}</span>}
      </label>

      <label>
        Username
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={submitting}
        />
        {errors.username && <span className="error">{errors.username}</span>}
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
