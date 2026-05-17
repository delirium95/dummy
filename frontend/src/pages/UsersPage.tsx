import { useMemo, useState } from 'react';
import { Modal } from '../components/Modal';
import { Pagination } from '../components/Pagination';
import { UserForm } from '../components/UserForm';
import { UserPostsModal } from '../components/UserPostsModal';
import { UsersTable } from '../components/UsersTable';
import {
  errorMessage,
  useCreateUserMutation,
  useDeleteUserMutation,
  useGetUsersQuery,
  useRunSyncMutation,
  useUpdateUserMutation,
  type ListQuery,
} from '../services/api';
import type { CreateUserRequest, SortDirection, User } from '../types/domain';

const DEFAULT_QUERY: ListQuery = {
  limit: 10,
  offset: 0,
  sort: 'id',
  direction: 'asc',
};

export function UsersPage(): JSX.Element {
  const [query, setQuery] = useState<ListQuery>(DEFAULT_QUERY);
  const { data: page, isLoading, isFetching, error } = useGetUsersQuery(query);

  const [createUser] = useCreateUserMutation();
  const [updateUser] = useUpdateUserMutation();
  const [deleteUser, { isLoading: deleting }] = useDeleteUserMutation();
  const [runSync, { isLoading: syncing }] = useRunSyncMutation();

  const [creating, setCreating] = useState<boolean>(false);
  const [editing, setEditing] = useState<User | null>(null);
  const [postsFor, setPostsFor] = useState<User | null>(null);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  const items = useMemo<User[]>(() => page?.items ?? [], [page]);

  function handleSortChange(field: string, direction: SortDirection): void {
    setQuery((q) => ({ ...q, sort: field, direction, offset: 0 }));
  }

  function handleOffsetChange(offset: number): void {
    setQuery((q) => ({ ...q, offset }));
  }

  async function handleCreate(body: CreateUserRequest): Promise<void> {
    await createUser(body).unwrap();
    setCreating(false);
  }

  async function handleUpdate(body: CreateUserRequest): Promise<void> {
    if (editing === null) return;
    await updateUser({ id: editing.id, body }).unwrap();
    setEditing(null);
  }

  async function handleDelete(user: User): Promise<void> {
    if (!window.confirm(`Delete user ${user.username}?`)) return;
    try {
      await deleteUser(user.id).unwrap();
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Failed to delete';
      window.alert(message);
    }
  }

  async function handleSync(): Promise<void> {
    setSyncMessage(null);
    try {
      const result = await runSync().unwrap();
      setSyncMessage(
        `Synced: +${result.users_added}/~${result.users_updated} users, +${result.posts_added}/~${result.posts_updated} posts` +
          (result.posts_skipped_missing_author > 0
            ? ` (${result.posts_skipped_missing_author} posts skipped)`
            : ''),
      );
    } catch (e: unknown) {
      if (typeof e === 'object' && e !== null && 'detail' in e) {
        const detail = (e as { detail?: unknown }).detail;
        setSyncMessage(`Sync failed: ${typeof detail === 'string' ? detail : 'unknown'}`);
      } else {
        setSyncMessage('Sync failed');
      }
    }
  }

  return (
    <main className="users-page">
      <header className="page-header">
        <h1>Users</h1>
        <div className="header-actions">
          <button type="button" onClick={() => setCreating(true)}>
            New user
          </button>
          <button type="button" onClick={handleSync} disabled={syncing}>
            {syncing ? 'Syncing…' : 'Sync from DummyJSON'}
          </button>
        </div>
      </header>

      {syncMessage && <div className="banner info">{syncMessage}</div>}
      {error && (
        <div className="banner error" role="alert">
          {errorMessage(error)}
        </div>
      )}

      {isLoading ? (
        <div className="state">Loading…</div>
      ) : items.length === 0 && !isFetching ? (
        <div className="state">No users yet. Click "Sync from DummyJSON" to fetch some.</div>
      ) : (
        <>
          <UsersTable
            users={items}
            sortField={query.sort}
            sortDirection={query.direction}
            onSortChange={handleSortChange}
            onEdit={(u) => setEditing(u)}
            onDelete={(u) => {
              if (!deleting) void handleDelete(u);
            }}
            onViewPosts={(u) => setPostsFor(u)}
          />
          {page && (
            <Pagination
              total={page.total}
              limit={page.limit}
              offset={page.offset}
              onChange={handleOffsetChange}
            />
          )}
          {isFetching && !isLoading && <div className="state subtle">Refreshing…</div>}
        </>
      )}

      <Modal open={creating} onClose={() => setCreating(false)}>
        {creating && <UserForm onSubmit={handleCreate} onCancel={() => setCreating(false)} />}
      </Modal>

      <Modal open={editing !== null} onClose={() => setEditing(null)}>
        {editing && (
          <UserForm user={editing} onSubmit={handleUpdate} onCancel={() => setEditing(null)} />
        )}
      </Modal>

      {postsFor && <UserPostsModal user={postsFor} onClose={() => setPostsFor(null)} />}
    </main>
  );
}
