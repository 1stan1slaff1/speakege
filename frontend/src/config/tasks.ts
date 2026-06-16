export interface RecordingSegment {
  label: string;
  seconds: number;
}

export interface TaskConfig {
  title: string;
  prepSeconds: number;
  recordSeconds: number;
  maxScore: number;
  description: string;
  recordingSegments: readonly RecordingSegment[];
}

export const TASK_CONFIG = {
  task1: {
    title: "Задание 1 — Чтение текста вслух",
    prepSeconds: 90,
    recordSeconds: 90,
    maxScore: 1,
    description: "Подготовьтесь и прочитайте научно-популярный текст вслух.",
    recordingSegments: [{ label: "Чтение текста", seconds: 90 }],
  },
  task2: {
    title: "Задание 2 — Условный диалог-расспрос",
    prepSeconds: 90,
    recordSeconds: 80,
    maxScore: 4,
    description: "Задайте 4 прямых вопроса по рекламному объявлению: по 20 секунд на каждый вопрос.",
    recordingSegments: [
      { label: "Вопрос 1", seconds: 20 },
      { label: "Вопрос 2", seconds: 20 },
      { label: "Вопрос 3", seconds: 20 },
      { label: "Вопрос 4", seconds: 20 },
    ],
  },
  task3: {
    title: "Задание 3 — Условное интервью",
    prepSeconds: 0,
    recordSeconds: 200,
    maxScore: 5,
    description: "Ответьте на 5 вопросов интервьюера: по 40 секунд на каждый ответ.",
    recordingSegments: [
      { label: "Ответ 1", seconds: 40 },
      { label: "Ответ 2", seconds: 40 },
      { label: "Ответ 3", seconds: 40 },
      { label: "Ответ 4", seconds: 40 },
      { label: "Ответ 5", seconds: 40 },
    ],
  },
  task4: {
    title: "Задание 4 — Голосовое сообщение другу",
    prepSeconds: 150,
    recordSeconds: 180,
    maxScore: 10,
    description: "Обоснуйте выбор двух фотографий для проекта и выразите своё мнение: 12–15 фраз.",
    recordingSegments: [{ label: "Голосовое сообщение", seconds: 180 }],
  },
} as const satisfies Record<string, TaskConfig>;

export type TaskType = keyof typeof TASK_CONFIG;
