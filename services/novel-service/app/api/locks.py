from fastapi import APIRouter, Depends, HTTPException

from app.schemas import (
    LockAcquireRequest,
    LockReleaseRequest,
    LockStatusResponse,
)
from app.services import lock_service

router = APIRouter()


@router.post("/acquire")
async def acquire_lock(req: LockAcquireRequest):
    acquired = await lock_service.acquire_lock(
        resource=req.resource,
        holder=req.holder,
        lock_type=req.lock_type,
        timeout=req.timeout,
    )
    if not acquired:
        status = await lock_service.get_lock_status(req.resource)
        raise HTTPException(
            status_code=409,
            detail={
                "message": "锁已被占用",
                "holder": status.get("holder"),
                "expires_at": status.get("expires_at"),
            },
        )
    return {"status": "acquired", "resource": req.resource}


@router.post("/release")
async def release_lock(req: LockReleaseRequest):
    released = await lock_service.release_lock(req.resource, req.holder)
    if not released:
        raise HTTPException(status_code=404, detail="锁不存在或持有者不匹配")
    return {"status": "released", "resource": req.resource}


@router.get("/status", response_model=LockStatusResponse)
async def get_lock_status(resource: str):
    status = await lock_service.get_lock_status(resource)
    return status
