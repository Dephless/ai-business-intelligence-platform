from pathlib import PurePosixPath

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate, AnalysisRead
from app.services.analysis_service import analyze_dataset
from app.services.csv_service import MAX_FILE_SIZE_BYTES, parse_csv

router = APIRouter(prefix="/analyses", tags=["analyses"])


def _save_analysis(
    dataset_name: str,
    records: list[dict],
    db: Session,
) -> Analysis:
    try:
        result = analyze_dataset(dataset_name, records)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Analysis provider failed.",
        ) from exc

    analysis = Analysis(
        dataset_name=dataset_name,
        record_count=len(records),
        result=result.model_dump(),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis


@router.post("", response_model=AnalysisRead, status_code=201)
def create_analysis(payload: AnalysisCreate, db: Session = Depends(get_db)):
    return _save_analysis(payload.dataset_name, payload.records, db)


@router.post("/upload", response_model=AnalysisRead, status_code=201)
async def upload_analysis(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required.")

    filename = PurePosixPath(file.filename.replace("\\", "/")).name

    if not filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    try:
        content = await file.read(MAX_FILE_SIZE_BYTES + 1)
    finally:
        await file.close()

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="The CSV file exceeds the 5 MB size limit.",
        )

    try:
        records = parse_csv(content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return _save_analysis(filename, records, db)


@router.get("/{analysis_id}", response_model=AnalysisRead)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis
