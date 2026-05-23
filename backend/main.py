from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

from matcher import find_matches
from image_utils import cartoonify_image

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / 'data' / 'temp'
DATABASE_DIR = BASE_DIR / 'data' / 'database'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title='LookAlike API', version='0.1.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:5173', 'http://localhost:5173'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# Serve static images
app.mount("/static", StaticFiles(directory=str(DATABASE_DIR)), name="static")

@app.get('/health')
def health_check():
    return {'status': 'ok'}

@app.post('/upload')
async def upload_image(mode: str = Form('human'), file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail='Le fichier doit être une image.')

    # Read file and enforce size limit
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f'Fichier trop volumineux ({len(contents) // (1024*1024)} MB). Maximum autorisé : {MAX_UPLOAD_SIZE // (1024*1024)} MB.'
        )

    ext = Path(file.filename).suffix or '.jpg'
    tmp_filename = f'{uuid.uuid4().hex}{ext}'
    tmp_path = UPLOAD_DIR / tmp_filename

    try:
        with tmp_path.open('wb') as buffer:
            buffer.write(contents)

        if mode in ['cartoon', 'anime']:
            cartoonify_image(str(tmp_path), str(tmp_path))

        matches = find_matches(str(tmp_path), mode=mode, top_k=3)
        return {'matches': matches}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass

