from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Body
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from workout_api.categorias.models import CategoriaModel
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut, CategoriaUpdate
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()


@router.post(
    path="/",
    summary="Criar nova Categoria",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoriaOut
)
async def post(db_session: DatabaseDependency, categoria_in: CategoriaIn = Body(...)) -> CategoriaOut:
    try:
        categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
        categoria_model = CategoriaModel(**categoria_out.model_dump())

        categoria_nome = categoria_model.nome

        db_session.add(categoria_model)
        await db_session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe uma categoria cadastrada com o nome: {categoria_nome}."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro não esperado ao inserir os dados no banco."
        )

    return categoria_out


@router.get(
    path="/",
    summary="Consultar todas as Categorias",
    status_code=status.HTTP_200_OK,
    response_model=list[CategoriaOut]
)
async def query(db_session: DatabaseDependency) -> list[CategoriaOut]:
    categorias: list[CategoriaOut] = (
        await db_session.execute(select(CategoriaModel))
    ).scalars().all()

    return categorias


@router.get(
    path="/{id}",
    summary="Consultar Categorias pelo id",
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut
)
async def get(id: UUID4, db_session: DatabaseDependency) -> CategoriaOut:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria não encontrada no id: {id}"
        )

    return categoria


@router.patch(
    path="/{id}",
    summary="Editar uma Categoria pelo id",
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut
)
async def update(
        id: UUID4,
        db_session: DatabaseDependency,
        categoria_up: CategoriaUpdate = Body(...)
) -> CategoriaOut:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria não encontrada no id: {id}"
        )

    categoria_update = categoria_up.model_dump(exclude_unset=True)
    for key, value in categoria_update.items():
        setattr(categoria, key, value)

    await db_session.commit()
    await db_session.refresh(categoria)

    return categoria


@router.delete(
    path="/{id}",
    summary="Deletar uma Categoria pelo id",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria não encontrada no id: {id}"
        )

    await db_session.delete(categoria)
    await db_session.commit()
