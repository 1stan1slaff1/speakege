from fastapi import APIRouter

from app.billing import FREE_REGISTERED_CREDITS, TASK_CREDIT_COST, get_full_exam_credit_cost
from app.models.schemas import BillingPublicInfo

router = APIRouter()


@router.get("/billing/public", response_model=BillingPublicInfo)
async def get_public_billing_info():
    return BillingPublicInfo(
        task_credit_cost=dict(TASK_CREDIT_COST),
        free_registered_credits=FREE_REGISTERED_CREDITS,
        full_exam_credit_cost=get_full_exam_credit_cost(),
        currency_label="кредиты",
    )
