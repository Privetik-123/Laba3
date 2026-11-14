import io
import os
import uuid

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import requests

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List

# ---------- Инициализация ----------
app = FastAPI(title="ЛР3 — Вариант 7")
os.makedirs("static/uploaded", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

RECAPTCHA_SITE = os.getenv("RECAPTCHA_SITE", "6LfTdh8uAAAAAPzAiPTmjYt4WBt8UlHVl3q4ZVah")
RECAPTCHA_SECRET = os.getenv(
    "RECAPTCHA_SECRET", "6LfTdh8uAAAAADKa9dXlHIFsNAxue1BXsbwTtcmw"
)


# ---------- Логика варианта 7 ----------
def reorder_channels(img: Image.Image, order: str) -> np.ndarray:
    if len(order) != 3 or sorted(order) != ["b", "g", "r"]:
        raise ValueError("Порядок должен быть перестановкой r,g,b (например, 'grb')")
    arr = np.array(img.convert("RGB"))
    idx = {"r": 0, "g": 1, "b": 2}
    new_idx = [idx[c] for c in order]
    return arr[..., new_idx]


def color_hist_figure(arr: np.ndarray, title: str) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(5, 3))
    for i, color in enumerate(["red", "green", "blue"]):
        ax.hist(arr[..., i].ravel(), bins=32, color=color, alpha=0.5, label=color)
    ax.set_title(title)
    ax.legend()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


def mean_profile_figure(arr: np.ndarray, axis: int, title: str) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(5, 3))
    for i, color in enumerate(["red", "green", "blue"]):
        ax.plot(arr[..., i].mean(axis=axis), color=color, label=color)
    ax.set_title(title)
    ax.legend()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


def verify_captcha(token: str) -> bool:
    if not token:
        return False
    r = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": RECAPTCHA_SECRET, "response": token},
        timeout=10,
    )
    return r.json().get("success", False)


# ---------- Маршруты ----------
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request, "forms.html", {"site_key": RECAPTCHA_SITE}
    )


@app.get("/image_form", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse(
        request, "forms.html", {"site_key": RECAPTCHA_SITE}
    )


@app.post("/image_form", response_class=HTMLResponse)
async def form_post(
    request: Request,
    order: str = Form(...),
    resp: str = Form(...),
    files: List[UploadFile] = File(...),
):
    if not verify_captcha(resp):
        raise HTTPException(status_code=400, detail="Ошибка проверки капчи")

    if not files or not files[0].filename:
        raise HTTPException(status_code=400, detail="Файл не загружен")

    content = await files[0].read()
    try:
        img = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Не удалось прочитать изображение")

    try:
        new_arr = reorder_channels(img, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    name = uuid.uuid4().hex
    orig_path = f"static/uploaded/orig_{name}.jpg"
    new_path = f"static/uploaded/new_{name}.jpg"
    img.save(orig_path)
    Image.fromarray(new_arr.astype(np.uint8)).save(new_path)

    orig_arr = np.array(img)
    figures = {
        "hist_orig": color_hist_figure(orig_arr, "Исходное — распределение цветов"),
        "hist_new": color_hist_figure(new_arr, "Новое — распределение цветов"),
        "meanV_orig": mean_profile_figure(
            orig_arr, 0, "Среднее по вертикали — исходное"
        ),
        "meanV_new": mean_profile_figure(new_arr, 0, "Среднее по вертикали — новое"),
        "meanH_orig": mean_profile_figure(
            orig_arr, 1, "Среднее по горизонтали — исходное"
        ),
        "meanH_new": mean_profile_figure(new_arr, 1, "Среднее по горизонтали — новое"),
    }
    for key, buf in figures.items():
        with open(f"static/uploaded/{key}_{name}.png", "wb") as f:
            f.write(buf.getvalue())

    return templates.TemplateResponse(
        request,
        "image.html",
        {
            "order": order,
            "name": name,
        },
    )
