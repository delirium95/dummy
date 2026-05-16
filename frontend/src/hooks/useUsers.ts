import { useCallback, useEffect, useState } from 'react';
import { usersApi, type ListUsersQuery } from '../api/users';
import { ApiError } from '../api/client';
import type { PageResponse, User } from '../types/domain';

export interface UseUsersResult {
  page: PageResponse<User> | null;
  loading: boolean;
  error: ApiError | null;
  reload: () => void;
}

export function useUsers(query: ListUsersQuery): UseUsersResult {
  const [page, setPage] = useState<PageResponse<User> | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [reloadKey, setReloadKey] = useState<number>(0);

  const reload = useCallback(() => {
    setReloadKey((n) => n + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    usersApi
      .list(query)
      .then((result) => {
        if (!cancelled) {
          setPage(result);
        }
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        if (e instanceof ApiError) {
          setError(e);
        } else if (e instanceof Error) {
          setError(new ApiError(0, 'network_error', e.message));
        } else {
          setError(new ApiError(0, 'unknown_error', 'Unknown error'));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [query.limit, query.offset, query.sort, query.direction, reloadKey]);

  return { page, loading, error, reload };
}
