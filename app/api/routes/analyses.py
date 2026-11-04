from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate, AnalysisRead
from app.services.analysis_service import analyze_dataset

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("", response_model=AnalysisRead, status_code=201)
def create_analysis(payload: AnalysisCreate, db: Session = Depends(get_db)):
    try:
        result = analyze_dataset(payload.dataset_name, payload.records)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Analysis provider failed.") from exc

    analysis = Analysis(
        dataset_name=payload.dataset_name,
        record_count=len(payload.records),
        result=result.model_dump(),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("/{analysis_id}", response_model=AnalysisRead)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis
