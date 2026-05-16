import { useMemo, useState } from 'react';
import { Modal } from '../components/Modal';
import { Pagination } from '../components/Pagination';
import { UserForm } from '../components/UserForm';
import { UsersTable } from '../components/UsersTable';
import { useUsers } from '../hooks/useUsers';
import { usersApi, type ListUsersQuery } from '../api/users';
import { syncApi } from '../api/sync';
import { ApiError } from '../api/client';
import type { SortDirection, UpdateUserRequest, User } from '../types/domain';

const DEFAULT_QUERY: ListUsersQuery = {
  limit: 10,
  offset: 0,
  sort: 'id',
  direction: 'asc',
};

export function UsersPage(): JSX.Element {
  const [query, setQuery] = useState<ListUsersQuery>(DEFAULT_QUERY);
  const { page, loading, error, reload } = useUsers(query);

  const [editing, setEditing] = useState<User | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);
  const [syncing, setSyncing] = useState<boolean>(false);

  const items = useMemo<User[]>(() => page?.items ?? [], [page]);

  function handleSortChange(field: string, direction: SortDirection): void {
    setQuery((q) => ({ ...q, sort: field, direction, offset: 0 }));
  }

  function handleOffsetChange(offset: number): void {
    setQuery((q) => ({ ...q, offset }));
  }

  async function handleSubmit(changes: UpdateUserRequest): Promise<void> {
    if (editing === null) return;
    await usersApi.update(editing.id, changes);
    setEditing(null);
    reload();
  }

  async function handleDelete(user: User): Promise<void> {
    if (!window.confirm(`Delete user ${user.username}?`)) return;
    setDeletingId(user.id);
    try {
      await usersApi.remove(user.id);
      reload();
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Failed to delete';
      window.alert(message);
    } finally {
      setDeletingId(null);
    }
  }

  async function handleSync(): Promise<void> {
    setSyncing(true);
    setSyncMessage(null);
    try {
      const result = await syncApi.run();
      setSyncMessage(
        `Synced: +${result.users_added}/~${result.users_updated} users, +${result.posts_added}/~${result.posts_updated} posts` +
          (result.posts_skipped_missing_author > 0
            ? ` (${result.posts_skipped_missing_author} posts skipped)`
            : ''),
      );
      reload();
    } catch (e: unknown) {
      if (e instanceof ApiError) {
        setSyncMessage(`Sync failed: ${e.detail || e.message}`);
      } else if (e instanceof Error) {
        setSyncMessage(`Sync failed: ${e.message}`);
      } else {
        setSyncMessage('Sync failed');
      }
    } finally {
      setSyncing(false);
    }
  }

  return (
    <main className="users-page">
      <header className="page-header">
        <h1>Users</h1>
        <div className="header-actions">
          <button type="button" onClick={handleSync} disabled={syncing}>
            {syncing ? 'Syncing…' : 'Sync from DummyJSON'}
          </button>
        </div>
      </header>

      {syncMessage && <div className="banner info">{syncMessage}</div>}
      {error && (
        <div className="banner error" role="alert">
          {error.detail || error.message}
        </div>
      )}

      {loading && page === null ? (
        <div className="state">Loading…</div>
      ) : items.length === 0 && !loading ? (
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
              if (deletingId !== u.id) {
                void handleDelete(u);
              }
            }}
          />
          {page !== null && (
            <Pagination
              total={page.total}
              limit={page.limit}
              offset={page.offset}
              onChange={handleOffsetChange}
            />
          )}
        </>
      )}

      <Modal open={editing !== null} onClose={() => setEditing(null)}>
        {editing && (
          <UserForm user={editing} onSubmit={handleSubmit} onCancel={() => setEditing(null)} />
        )}
      </Modal>
    </main>
  );
}
