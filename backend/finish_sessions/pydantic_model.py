from typing import List, Type, Union, Optional
from pydantic import BaseModel, create_model

# Modelo base de Pydantic para validar el JSON


class DynamicModel(BaseModel):
    @classmethod
    def create_dynamic_model(cls, fields: List[str]) -> Type["DynamicModel"]:
        # Definimos un modelo con campos dinámicos que pueden ser tanto str como int o float,
        # pero almacenados siempre como str.
        attributes = {
            field: (Optional[Union[str, int, float]], ...) for field in fields
        }
        return create_model("DynamicModel", **attributes)
