import type { SortDirection } from '@/types/domain';

interface Props {
  label: string;
  field: string;
  activeField: string;
  direction: SortDirection;
  onChange: (field: string, direction: SortDirection) => void;
}

export function SortableHeader({
  label,
  field,
  activeField,
  direction,
  onChange,
}: Props): JSX.Element {
  const isActive = activeField === field;
  const nextDirection: SortDirection = isActive && direction === 'asc' ? 'desc' : 'asc';
  const indicator = isActive ? (direction === 'asc' ? ' ▲' : ' ▼') : '';

  return (
    <th>
      <button
        type="button"
        className="sort-button"
        onClick={() => onChange(field, nextDirection)}
        aria-label={`Sort by ${label}`}
      >
        {label}
        {indicator}
      </button>
    </th>
  );
}
