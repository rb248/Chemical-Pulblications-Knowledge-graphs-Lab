from datetime import date

from app.schemes.model_info_scheme import ModelInfo

model_info_obj = ModelInfo(
    name="Flowsheet recognition model", modelVersion="v_01", date=date(2022, 1, 1),
    author=["Lukas Schulze Balhorn", "Qinghe Gao", "Dominik Goldstein", "Artur M. Schweidtmann"],
    references=["https://doi.org/10.1016/B978-0-323-85159-6.50261-X"]
)
