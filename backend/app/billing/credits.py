from types import MappingProxyType

# Keep pricing separate from rubrics/max scores.
# This lets us quickly change monetization without touching exam scoring logic.
TASK_CREDIT_COST = MappingProxyType({
    "task1": 2,
    "task2": 4,
    "task3": 5,
    "task4": 8,
})

FREE_REGISTERED_CREDITS = 40


def get_task_credit_cost(task_type: str) -> int:
    try:
        return TASK_CREDIT_COST[task_type]
    except KeyError as exc:
        raise ValueError(f"Unknown task type: {task_type}") from exc


def get_full_exam_credit_cost() -> int:
    return sum(TASK_CREDIT_COST.values())
