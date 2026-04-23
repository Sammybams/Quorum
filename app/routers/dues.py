from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..payments import PaymentInitializationError, initialize_paystack_transaction, payment_callback_url
from ..rbac import require_workspace_permission

router = APIRouter(prefix="/workspaces/{workspace_id}/dues-cycles", tags=["dues"])


@router.post("", response_model=schemas.DuesCycleOut)
def create_dues_cycle(
    workspace_id: int,
    payload: schemas.DuesCycleCreate,
    db: Session = Depends(get_db),
    _membership: models.WorkspaceMember = Depends(require_workspace_permission("dues.manage")),
):
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    cycle = models.DuesCycle(workspace_id=workspace_id, **payload.model_dump())
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return cycle


@router.get("", response_model=list[schemas.DuesCycleOut])
def list_dues_cycles(workspace_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.DuesCycle)
        .filter(models.DuesCycle.workspace_id == workspace_id)
        .order_by(models.DuesCycle.created_at.desc())
        .all()
    )


payments_router = APIRouter(prefix="/workspaces/{workspace_id}/dues-payments", tags=["dues"])


@payments_router.get("", response_model=list[schemas.DuesPaymentOut])
def list_dues_payments(workspace_id: int, db: Session = Depends(get_db)):
    payments = (
        db.query(models.DuesPayment)
        .filter(models.DuesPayment.workspace_id == workspace_id)
        .order_by(models.DuesPayment.created_at.desc())
        .all()
    )
    return [_payment_out(payment) for payment in payments]


@router.post("/{cycle_id}/payments/manual", response_model=schemas.DuesPaymentOut, status_code=201)
def create_manual_payment(
    workspace_id: int,
    cycle_id: int,
    payload: schemas.DuesPaymentCreate,
    db: Session = Depends(get_db),
    _membership: models.WorkspaceMember = Depends(require_workspace_permission("dues.manage")),
):
    cycle = (
        db.query(models.DuesCycle)
        .filter(models.DuesCycle.workspace_id == workspace_id, models.DuesCycle.id == cycle_id)
        .first()
    )
    if not cycle:
        raise HTTPException(status_code=404, detail="Dues cycle not found")

    payment = models.DuesPayment(
        workspace_id=workspace_id,
        cycle_id=cycle_id,
        member_id=payload.member_id,
        amount=payload.amount,
        method=payload.method,
        gateway_ref=payload.gateway_ref,
        receipt_url=payload.receipt_url,
        status="pending" if payload.method == "manual" else "initiated",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return _payment_out(payment)


@router.post("/{cycle_id}/payments/checkout", response_model=schemas.DuesPaymentCheckoutResponse, status_code=201)
def initialize_dues_checkout(
    workspace_id: int,
    cycle_id: int,
    payload: schemas.DuesPaymentCheckoutCreate,
    db: Session = Depends(get_db),
    _membership: models.WorkspaceMember = Depends(require_workspace_permission("dues.manage")),
):
    cycle = (
        db.query(models.DuesCycle)
        .filter(models.DuesCycle.workspace_id == workspace_id, models.DuesCycle.id == cycle_id)
        .first()
    )
    if not cycle:
        raise HTTPException(status_code=404, detail="Dues cycle not found")

    member = None
    if payload.member_id:
        member = (
            db.query(models.WorkspaceMember)
            .filter(
                models.WorkspaceMember.workspace_id == workspace_id,
                models.WorkspaceMember.id == payload.member_id,
            )
            .first()
        )
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

    email = payload.email or (member.user.email if member and member.user else None)
    amount = payload.amount or cycle.amount
    reference = f"QRM-DUES-{uuid4().hex[:14].upper()}"
    checkout = None
    if email:
        try:
            checkout = initialize_paystack_transaction(
                email=email,
                amount=amount,
                reference=reference,
                callback_url=payment_callback_url(f"/workspaces/{workspace_id}/dues"),
                metadata={
                    "type": "dues_payment",
                    "workspace_id": workspace_id,
                    "cycle_id": cycle_id,
                    "member_id": payload.member_id,
                },
            )
        except PaymentInitializationError as exc:
            raise HTTPException(status_code=502, detail=f"Unable to initialize payment: {exc}") from exc

    payment = models.DuesPayment(
        workspace_id=workspace_id,
        cycle_id=cycle_id,
        member_id=payload.member_id,
        amount=amount,
        method="paystack" if checkout else "manual",
        gateway_ref=reference,
        status="initiated" if checkout else "pending",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return schemas.DuesPaymentCheckoutResponse(
        payment=_payment_out(payment),
        payment_reference=reference,
        checkout_url=checkout.authorization_url if checkout else None,
        access_code=checkout.access_code if checkout else None,
    )


@payments_router.post("/{payment_id}/confirm", response_model=schemas.DuesPaymentOut)
def confirm_dues_payment(
    workspace_id: int,
    payment_id: int,
    db: Session = Depends(get_db),
    membership: models.WorkspaceMember = Depends(require_workspace_permission("dues.confirm_payment")),
):
    payment = (
        db.query(models.DuesPayment)
        .filter(models.DuesPayment.workspace_id == workspace_id, models.DuesPayment.id == payment_id)
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Dues payment not found")

    payment.status = "paid"
    payment.confirmed_by_user_id = membership.user_id
    payment.confirmed_at = datetime.utcnow()
    if payment.member:
        payment.member.dues_status = "paid"
    db.commit()
    db.refresh(payment)
    return _payment_out(payment)


def _payment_out(payment: models.DuesPayment) -> schemas.DuesPaymentOut:
    return schemas.DuesPaymentOut(
        id=payment.id,
        workspace_id=payment.workspace_id,
        cycle_id=payment.cycle_id,
        member_id=payment.member_id,
        member_name=payment.member.user.full_name if payment.member and payment.member.user else None,
        amount=payment.amount,
        method=payment.method,
        gateway_ref=payment.gateway_ref,
        receipt_url=payment.receipt_url,
        status=payment.status,
        confirmed_by_user_id=payment.confirmed_by_user_id,
        confirmed_at=payment.confirmed_at,
        created_at=payment.created_at,
    )
