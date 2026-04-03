from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

router = APIRouter(prefix="/uploads", tags=["Uploads"])

BASE_STATIC_DIR = Path("app/ui/static")
CENTERS_DIR = BASE_STATIC_DIR / "centers"
STUDENTS_DIR = BASE_STATIC_DIR / "students"

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _validate_image(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no tiene nombre.",
        )

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no permitido. Use JPG, JPEG, PNG o WEBP.",
        )

    return extension


def _save_upload(file: UploadFile, target_dir: Path, prefix: str) -> str:
    extension = _validate_image(file)

    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{prefix}_{uuid4().hex}{extension}"
    destination = target_dir / filename

    try:
        with destination.open("wb") as buffer:
            buffer.write(file.file.read())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudo guardar el archivo: {exc}",
        ) from exc
    finally:
        file.file.close()

    relative_path = destination.relative_to(BASE_STATIC_DIR).as_posix()
    return f"/static/{relative_path}"


@router.post("/centers/logo")
def upload_center_logo(file: UploadFile = File(...)):
    file_url = _save_upload(file, CENTERS_DIR / "logos", "center_logo")
    return {
        "message": "Logo subido correctamente.",
        "file_url": file_url,
    }


@router.post("/centers/letterhead")
def upload_center_letterhead(file: UploadFile = File(...)):
    file_url = _save_upload(file, CENTERS_DIR / "letterheads", "center_letterhead")
    return {
        "message": "Membrete subido correctamente.",
        "file_url": file_url,
    }


@router.post("/students/photo")
def upload_student_photo(file: UploadFile = File(...)):
    file_url = _save_upload(file, STUDENTS_DIR / "photos", "student_photo")
    return {
        "message": "Foto subida correctamente.",
        "file_url": file_url,
    }