import { apiClient } from './client';
import type { SyncResult } from '../types/domain';

export const syncApi = {
  run(): Promise<SyncResult> {
    return apiClient.post<SyncResult>('/sync', {});
  },
};
