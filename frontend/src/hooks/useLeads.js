import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getLeads, createLead, seedDemoLeads, getDashboardStats, getRmQueue, getCallDetail, updateRmStatus } from '../lib/api';

export function useLeads(params) {
  return useQuery({
    queryKey: ['leads', params],
    queryFn: () => getLeads(params),
  });
}

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: getDashboardStats,
  });
}

export function useRmQueue() {
  return useQuery({
    queryKey: ['rm-queue'],
    queryFn: getRmQueue,
  });
}

export function useCallDetail(callId) {
  return useQuery({
    queryKey: ['call-detail', callId],
    queryFn: () => getCallDetail(callId),
    enabled: !!callId,
  });
}

export function useCreateLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createLead,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['leads'] });
      qc.invalidateQueries({ queryKey: ['dashboard-stats'] });
    },
  });
}

export function useSeedDemo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: seedDemoLeads,
    onSuccess: () => {
      setTimeout(() => {
        qc.invalidateQueries({ queryKey: ['leads'] });
        qc.invalidateQueries({ queryKey: ['dashboard-stats'] });
        qc.invalidateQueries({ queryKey: ['rm-queue'] });
      }, 5000);
    },
  });
}

export function useUpdateRmStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }) => updateRmStatus(id, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['rm-queue'] });
    },
  });
}
