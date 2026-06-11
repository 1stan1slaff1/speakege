export const TASK_CONFIG = {
  task1: {
    title: "Чтение вслух",
    prepSeconds: 90,      // 1.5 minutes
    recordSeconds: 120,   // 2 minutes
    description: "Подготовьте и прочитайте текст вслух",
  },
  task2: {
    title: "Составление вопросов",
    prepSeconds: 90,
    recordSeconds: 120,
    description: "Задайте 5 вопросов по теме",
  },
  task3: {
    title: "Монолог по фотографии",
    prepSeconds: 90,
    recordSeconds: 120,
    description: "Опишите фотографию и сравните с личным опытом",
  },
  task4: {
    title: "Диалог-расспрос",
    prepSeconds: 0,
    recordSeconds: 180,
    description: "Ответьте на вопросы экзаменатора",
  },
} as const;

export type TaskType = keyof typeof TASK_CONFIG;
