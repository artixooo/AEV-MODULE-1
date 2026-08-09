from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.policy_models import Policy
from app.schemas.policy_schemas import PolicyCreate, PolicyUpdate, PolicyResponse
from app.services.cache_service import cache_service

router = APIRouter(prefix="/policies", tags=["ABAC Policies"])


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
def create_policy(policy_in: PolicyCreate, db: Session = Depends(get_db)):
    existing = db.query(Policy).filter(Policy.policy_code == policy_in.policy_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Policy code '{policy_in.policy_code}' already exists")

    policy = Policy(**policy_in.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    cache_service.invalidate_all()
    return policy


@router.get("", response_model=List[PolicyResponse])
def list_policies(db: Session = Depends(get_db)):
    return db.query(Policy).filter(Policy.status == "ACTIVE").all()


@router.get("/{policy_id}", response_model=PolicyResponse)
def get_policy(policy_id: str, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.put("/{policy_id}", response_model=PolicyResponse)
def update_policy(policy_id: str, policy_in: PolicyUpdate, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    update_data = policy_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(policy, field, value)

    db.commit()
    db.refresh(policy)
    cache_service.invalidate_all()
    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(policy_id: str, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    policy.status = "DELETED"
    db.commit()
    cache_service.invalidate_all()
    return None
