import type { TaskType } from '@/config/tasks';

export const DEFAULT_TASK_CREDIT_COST: Record<TaskType, number> = {
  task1: 2,
  task2: 4,
  task3: 5,
  task4: 8,
};

export const DEFAULT_FREE_REGISTERED_CREDITS = 40;
export const DEFAULT_CURRENCY_LABEL = 'кредиты';

export interface BillingPublicInfo {
  task_credit_cost: Record<TaskType, number>;
  free_registered_credits: number;
  full_exam_credit_cost: number;
  currency_label: string;
}
