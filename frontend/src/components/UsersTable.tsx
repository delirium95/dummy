import type { SortDirection, User } from '@/types/domain';
import { SortableHeader } from '@/components/SortableHeader';

interface Props {
  users: User[];
  sortField: string;
  sortDirection: SortDirection;
  onSortChange: (field: string, direction: SortDirection) => void;
  onEdit: (user: User) => void;
  onDelete: (user: User) => void;
  onViewPosts: (user: User) => void;
}

const COLUMNS: { label: string; field: string }[] = [
  { label: 'ID', field: 'id' },
  { label: 'First name', field: 'first_name' },
  { label: 'Last name', field: 'last_name' },
  { label: 'Email', field: 'email' },
  { label: 'Username', field: 'username' },
];

export function UsersTable({
  users,
  sortField,
  sortDirection,
  onSortChange,
  onEdit,
  onDelete,
  onViewPosts,
}: Props): JSX.Element {
  return (
    <table className="users-table">
      <thead>
        <tr>
          {COLUMNS.map((c) => (
            <SortableHeader
              key={c.field}
              label={c.label}
              field={c.field}
              activeField={sortField}
              direction={sortDirection}
              onChange={onSortChange}
            />
          ))}
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {users.map((u) => (
          <tr key={u.id}>
            <td>{u.id}</td>
            <td>{u.first_name}</td>
            <td>{u.last_name}</td>
            <td>{u.email}</td>
            <td>{u.username}</td>
            <td className="actions">
              <button type="button" onClick={() => onViewPosts(u)}>
                Posts
              </button>
              <button type="button" onClick={() => onEdit(u)}>
                Edit
              </button>
              <button type="button" className="danger" onClick={() => onDelete(u)}>
                Delete
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
