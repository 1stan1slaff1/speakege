from app.rubrics.task1 import TASK1_RUBRIC
from app.rubrics.task2 import TASK2_RUBRIC
from app.rubrics.task3 import TASK3_RUBRIC
from app.rubrics.task4 import TASK4_RUBRIC

RUBRICS = {
    "task1": TASK1_RUBRIC,
    "task2": TASK2_RUBRIC,
    "task3": TASK3_RUBRIC,
    "task4": TASK4_RUBRIC,
}

MAX_TOTALS = {
    "task1": 1,
    "task2": 4,
    "task3": 5,
    "task4": 10,
}

def get_rubric(task_type: str) -> str:
    rubric = RUBRICS.get(task_type)
    if not rubric:
        raise ValueError(f"Unknown task type: {task_type}")
    return rubric

def get_max_total(task_type: str) -> int:
    max_total = MAX_TOTALS.get(task_type)
    if max_total is None:
        raise ValueError(f"Unknown task type: {task_type}")
    return max_total
