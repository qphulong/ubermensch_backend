from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.db.session import get_db
from src.schemas.search_engine import (
    PageRegisterInput,
    PageRegisterResponse,
    SearchQuery,
    SearchResponse,
    PageUnregister,
    PageUnregisterResponse,
)
from src.services.search_engine import register_page, search_pages, delete_page

router = APIRouter(prefix="/pages", tags=["pages"])


@router.post("/register", response_model=PageRegisterResponse)
def register_endpoint(
    payload: PageRegisterInput,
    db: Session = Depends(get_db),
):
    """
    HTTP ➞ service.register_page ➞ returns { id, success }
    """
    try:
        page_id = register_page(db, payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return PageRegisterResponse(id=page_id, success=True)


@router.post("/search", response_model=SearchResponse)
def search_endpoint(
    payload: SearchQuery,
    db: Session = Depends(get_db),
):
    """
    HTTP ➞ service.search_pages ➞ returns nearest neighbors
    """
    try:
        hits = search_pages(db, payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return SearchResponse(results=hits)

# TODO: can quyen admin cho api nay
@router.delete("/delete", response_model=PageUnregisterResponse)
def unregister_page(
    payload: PageUnregister,
    db: Session = Depends(get_db),
):
    page = delete_page(db, payload.id)

    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page with id '{payload.id}' not found.",
        )

    return PageUnregisterResponse(
        id=page.id,
        author=page.author,
        local_url=page.local_url,
        success=True,
    )
