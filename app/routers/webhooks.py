import hashlib
import hmac
import json
import os
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/paystack")
async def paystack_webhook(
    request: Request,
    x_paystack_signature: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    raw_body = await request.body()
    secret_key = os.getenv("PAYSTACK_SECRET_KEY")
    if secret_key:
        expected = hmac.new(secret_key.encode("utf-8"), raw_body, hashlib.sha512).hexdigest()
        if not x_paystack_signature or not hmac.compare_digest(expected, x_paystack_signature):
            raise HTTPException(status_code=401, detail="Invalid Paystack signature")

    payload = json.loads(raw_body.decode("utf-8"))
    event = payload.get("event")
    data = payload.get("data") or {}
    reference = data.get("reference")

    if event != "charge.success" or not reference:
        return {"status": "ignored"}

    payment = db.query(models.DuesPayment).filter(models.DuesPayment.gateway_ref == reference).first()
    if payment:
        payment.status = "paid"
        payment.method = "paystack"
        payment.confirmed_at = datetime.utcnow()
        if payment.member:
            payment.member.dues_status = "paid"
        db.commit()

        return {"status": "processed", "payment_id": payment.id}

    contribution = db.query(models.Contribution).filter(models.Contribution.gateway_ref == reference).first()
    if not contribution:
        raise HTTPException(status_code=404, detail="Payment reference not found")

    if contribution.status != "confirmed":
        contribution.status = "confirmed"
        contribution.method = "paystack"
        contribution.confirmed_at = datetime.utcnow()
        contribution.campaign.raised_amount += contribution.amount
        db.commit()

    return {"status": "processed", "contribution_id": contribution.id}
