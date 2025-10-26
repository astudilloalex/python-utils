from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import tempfile

from utils.excel.cleaner import ExcelCleaner

app = FastAPI(title="Excel Tools API", version="1.0.0")

@app.post("/excel/clean")
async def clean_excel(
    file: UploadFile = File(...),
    name_column: str | None = Form(None),
    sheet_name: str = Form("cleaned"),
):
    # Persist upload to temp
    tmp_in = Path(tempfile.gettempdir()) / f"upload_{file.filename}"
    with tmp_in.open("wb") as f:
        f.write(await file.read())

    out_path = tmp_in.with_name(tmp_in.stem + "_clean.xlsx")

    cleaner = ExcelCleaner()
    stats = cleaner.process_file(str(tmp_in), str(out_path), sheet_name=sheet_name, name_column=name_column)

    return JSONResponse({
        "out_path": str(out_path),
        "stats": {
            "original_rows": stats.original_rows,
            "rows_removed": stats.rows_removed,
            "rows_remaining": stats.rows_remaining,
            "detected_name_column": stats.detected_name_column,
            "detected_month_columns": stats.detected_month_columns,
        }
    })

from fastapi import FastAPI, UploadFile, File
import pandas as pd
from io import BytesIO

app = FastAPI()

@app.post("/merge-excel")
async def merge_excel(file: UploadFile = File(...)):
    # Leer todas las hojas
    content = await file.read()
    excel = pd.ExcelFile(BytesIO(content))

    all_data = []

    # Iterar sobre todas las hojas (años)
    for sheet_name in excel.sheet_names:
        df = pd.read_excel(excel, sheet_name=sheet_name)
        df["Year"] = sheet_name  # Guardar el año
        all_data.append(df)

    # Concatenar todos los años
    combined = pd.concat(all_data, ignore_index=True)

    # Asegurar columnas fijas
    id_cols = ["Code", "Name", "Type", "Group"]

    # Detectar las columnas de meses (todas las demás excepto las de identificación)
    month_cols = [c for c in combined.columns if c not in id_cols + ["Year"]]

    # Crear nuevas columnas como "ene-20", "feb-20", etc.
    melted = combined.melt(id_vars=id_cols + ["Year"], value_vars=month_cols,
                           var_name="Month", value_name="Value")

    melted["MonthYear"] = melted["Month"].astype(str) + "-" + melted["Year"].astype(str).str[-2:]

    # Pivotear para tener una fila por Name
    final = (
        melted
        .pivot_table(index=id_cols, columns="MonthYear", values="Value", aggfunc="first")
        .reset_index()
    )

    # Ordenar columnas cronológicamente
    sorted_cols = id_cols + sorted([c for c in final.columns if c not in id_cols])
    final = final[sorted_cols]

    # Exportar resultado
    final.to_excel('consolidado.xlsx', index=False)

    return {
        "message": "Archivo combinado correctamente",
        "columns": list(final.columns),
        "rows": len(final)
    }

