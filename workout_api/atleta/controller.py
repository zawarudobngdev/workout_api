from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Body, Query
from fastapi_pagination import Page, paginate
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from workout_api.atleta.models import AtletaModel
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate, AtletaCustomGet
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()


@router.post(
    path="/",
    summary="Criar um novo atleta",
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
)
async def post(db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...)):
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome

    categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_nome))
                 ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A categoria {categoria_nome} não foi encontrada."
        )

    centro_treinamento = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))
                          ).scalars().first()

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O Centro de Treinamento {centro_treinamento_nome} não foi encontrado."
        )

    try:
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.now(), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))

        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        atleta_cpf = atleta_model.cpf

        db_session.add(atleta_model)
        await db_session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um atleta cadastrado com o CPF: {atleta_cpf}."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro não esperado ao inserir os dados no banco."
        )

    return atleta_out


@router.get(
    path="/",
    summary="Consultar todos os Atletas",
    status_code=status.HTTP_200_OK,
    response_model=Page[AtletaCustomGet]
)
async def get_all(
        db_session: DatabaseDependency,
        nome: Optional[str] = Query(None),
        cpf: Optional[str] = Query(None)
) -> Page[AtletaCustomGet]:
    query = select(AtletaModel)

    if nome:
        query = query.filter_by(nome=nome)
    elif cpf:
        query = query.filter_by(cpf=cpf)

    atletas = (await db_session.execute(query)).scalars().all()

    all_atletas = [AtletaCustomGet.model_validate(atleta) for atleta in atletas]
    return paginate(all_atletas)


@router.get(
    path="/{id}",
    summary="Consultar um Atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut
)
async def get(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id, ))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}")

    return atleta


@router.patch(
    path="/{id}",
    summary="Editar um Atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut
)
async def update(
        id: UUID4,
        db_session: DatabaseDependency,
        atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}"
        )

    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.delete(
    path="/{id}",
    summary="Deletar um Atleta pelo id",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}"
        )

    await db_session.delete(atleta)
    await db_session.commit()
