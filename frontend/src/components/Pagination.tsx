interface Props {
  total: number;
  limit: number;
  offset: number;
  onChange: (offset: number) => void;
}

export function Pagination({ total, limit, offset, onChange }: Props): JSX.Element {
  const page = Math.floor(offset / limit) + 1;
  const pages = Math.max(1, Math.ceil(total / limit));
  const canPrev = offset > 0;
  const canNext = offset + limit < total;

  return (
    <nav className="pagination" aria-label="Pagination">
      <button
        type="button"
        onClick={() => onChange(Math.max(0, offset - limit))}
        disabled={!canPrev}
      >
        ← Prev
      </button>
      <span>
        Page {page} of {pages} ({total} total)
      </span>
      <button type="button" onClick={() => onChange(offset + limit)} disabled={!canNext}>
        Next →
      </button>
    </nav>
  );
}
