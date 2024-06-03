from typing import Annotated, Optional

from pydantic import Field, UUID4

from workout_api.contrib.schemas import BaseSchema


class CentroTreinamentoIn(BaseSchema):
    nome: Annotated[str, Field(description='Nome do centro de treinamento', example='CT King', max_length=20)]
    endereco: Annotated[
        str, Field(description='Endereço do centro de treinamento', example='Rua X, Q02', max_length=60)]
    proprietario: Annotated[
        str, Field(description='Proprietário do centro de treinamento', example='Marcos', max_length=50)]


class CentroTreinamentoOut(CentroTreinamentoIn):
    id: Annotated[UUID4, Field(description="Identificador do centro de treinamento")]


class CentroTreinamentoAtleta(BaseSchema):
    nome: Annotated[str, Field(description='Nome do centro de treinamento', example='CT King', max_length=20)]


class CentroTreinamentoUpdate(BaseSchema):
    nome: Annotated[
        Optional[str], Field(None, description='Nome do centro de treinamento', example='CT King', max_length=20)]
