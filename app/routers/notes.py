from fastapi import APIRouter, HTTPException, status

from app.deps import CurrentUser, DB
from app.models import Note, Role, User
from app.schemas import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


def _get_note_in_tenant(db: DB, note_id: int, user: User) -> Note:
    note = db.get(Note, note_id)
    # Treat cross-tenant access as not-found so tenants can't probe each other.
    if note is None or note.tenant_id != user.tenant_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "note not found")
    return note


def _can_modify(note: Note, user: User) -> bool:
    return note.owner_id == user.id or user.role == Role.admin


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(body: NoteCreate, user: CurrentUser, db: DB):
    note = Note(
        tenant_id=user.tenant_id,
        owner_id=user.id,
        title=body.title,
        content=body.content,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("", response_model=list[NoteOut])
def list_notes(user: CurrentUser, db: DB):
    return (
        db.query(Note)
        .filter(Note.tenant_id == user.tenant_id)
        .order_by(Note.created_at.desc())
        .all()
    )


@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: int, user: CurrentUser, db: DB):
    return _get_note_in_tenant(db, note_id, user)


@router.put("/{note_id}", response_model=NoteOut)
def update_note(note_id: int, body: NoteUpdate, user: CurrentUser, db: DB):
    note = _get_note_in_tenant(db, note_id, user)
    if not _can_modify(note, user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "not your note")
    note.title = body.title
    note.content = body.content
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, user: CurrentUser, db: DB):
    note = _get_note_in_tenant(db, note_id, user)
    if not _can_modify(note, user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "not your note")
    db.delete(note)
    db.commit()
