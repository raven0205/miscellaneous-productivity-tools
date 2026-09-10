from __future__ import annotations

import os
import re

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Float, ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool

DEFAULT_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./expense_splitter.db")


class Base(DeclarativeBase):
    pass


class Member(BaseModel):
    id: str
    name: str


class ExpenseSplit(BaseModel):
    member_id: str
    amount: float


class Expense(BaseModel):
    id: str
    description: str
    total_amount: float
    payer_id: str
    splits: list[ExpenseSplit]


class Group(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    name: str
    members: list[Member] = Field(default_factory=list)
    expenses: list[Expense] = Field(default_factory=list)


class CreateGroupRequest(BaseModel):
    name: str = Field(..., min_length=1)


class CreateMemberRequest(BaseModel):
    name: str = Field(..., min_length=1)


class CreateExpenseRequest(BaseModel):
    description: str = Field(..., min_length=1)
    total_amount: float = Field(..., gt=0)
    payer_id: str = Field(..., min_length=1)
    splits: list[ExpenseSplit] = Field(...)


class ReceiptParseRequest(BaseModel):
    receipt_text: str = Field(..., min_length=1)


class ReceiptParseResponse(BaseModel):
    description: str
    total_amount: float


class GroupRecord(Base):
    __tablename__ = 'groups'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    members: Mapped[list['MemberRecord']] = relationship(back_populates='group', cascade='all, delete-orphan')
    expenses: Mapped[list['ExpenseRecord']] = relationship(back_populates='group', cascade='all, delete-orphan')


class MemberRecord(Base):
    __tablename__ = 'members'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    group_id: Mapped[str] = mapped_column(ForeignKey('groups.id'), nullable=False)
    group: Mapped[GroupRecord] = relationship(back_populates='members')


class ExpenseRecord(Base):
    __tablename__ = 'expenses'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    payer_id: Mapped[str] = mapped_column(String, nullable=False)
    group_id: Mapped[str] = mapped_column(ForeignKey('groups.id'), nullable=False)
    group: Mapped[GroupRecord] = relationship(back_populates='expenses')
    splits: Mapped[list['ExpenseSplitRecord']] = relationship(back_populates='expense', cascade='all, delete-orphan')


class ExpenseSplitRecord(Base):
    __tablename__ = 'expense_splits'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    expense_id: Mapped[str] = mapped_column(ForeignKey('expenses.id'), nullable=False)
    member_id: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    expense: Mapped[ExpenseRecord] = relationship(back_populates='splits')


class DatabaseRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def seed_default_data(self) -> None:
        with self._session_factory() as session:
            if session.scalar(select(GroupRecord.id).limit(1)) is not None:
                return

            group = GroupRecord(id='group-trip', name='Weekend Trip')
            session.add(group)
            session.flush()

            session.add_all(
                [
                    MemberRecord(id='member-alice', name='Alice', group_id=group.id),
                    MemberRecord(id='member-ben', name='Ben', group_id=group.id),
                    MemberRecord(id='member-chloe', name='Chloe', group_id=group.id),
                ]
            )
            session.flush()

            expense_1 = ExpenseRecord(
                id='expense-1',
                description='Dinner at Sunset Bistro',
                total_amount=150,
                payer_id='member-alice',
                group_id=group.id,
            )
            session.add(expense_1)
            session.flush()
            session.add_all(
                [
                    ExpenseSplitRecord(expense_id=expense_1.id, member_id='member-alice', amount=50),
                    ExpenseSplitRecord(expense_id=expense_1.id, member_id='member-ben', amount=50),
                    ExpenseSplitRecord(expense_id=expense_1.id, member_id='member-chloe', amount=50),
                ]
            )

            expense_2 = ExpenseRecord(
                id='expense-2',
                description='Train tickets',
                total_amount=90,
                payer_id='member-ben',
                group_id=group.id,
            )
            session.add(expense_2)
            session.flush()
            session.add_all(
                [
                    ExpenseSplitRecord(expense_id=expense_2.id, member_id='member-alice', amount=30),
                    ExpenseSplitRecord(expense_id=expense_2.id, member_id='member-ben', amount=30),
                    ExpenseSplitRecord(expense_id=expense_2.id, member_id='member-chloe', amount=30),
                ]
            )

            session.commit()

    def get_groups(self) -> list[Group]:
        with self._session_factory() as session:
            records = session.scalars(select(GroupRecord).order_by(GroupRecord.id)).all()
            return [self._group_record_to_schema(record) for record in records]

    def create_group(self, name: str) -> Group:
        with self._session_factory() as session:
            group_count = len(session.scalars(select(GroupRecord)).all())
            group = GroupRecord(id=f'group-{group_count + 1}', name=name)
            session.add(group)
            session.commit()
            session.refresh(group)
            return self._group_record_to_schema(group)

    def get_group(self, group_id: str) -> GroupRecord | None:
        with self._session_factory() as session:
            return session.get(GroupRecord, group_id)

    def add_member(self, group_id: str, name: str) -> Member:
        with self._session_factory() as session:
            group = self._get_group_or_raise(session, group_id)
            normalized = name.strip()

            if not normalized:
                raise ValueError('Member name is required.')

            if any(member.name.lower() == normalized.lower() for member in group.members):
                raise ValueError('A participant with that name already exists.')

            member = MemberRecord(id=f"member-{len(group.members) + 1}", name=normalized, group_id=group.id)
            session.add(member)
            session.commit()
            session.refresh(member)
            return Member(id=member.id, name=member.name)

    def add_expense(self, group_id: str, payload: CreateExpenseRequest) -> Expense:
        with self._session_factory() as session:
            group = self._get_group_or_raise(session, group_id)

            if not group.members:
                raise ValueError('Add at least one participant before logging an expense.')

            if payload.payer_id not in {member.id for member in group.members}:
                raise ValueError('Unknown payer_id.')

            expense = ExpenseRecord(
                id=f"expense-{len(group.expenses) + 1}",
                description=payload.description,
                total_amount=payload.total_amount,
                payer_id=payload.payer_id,
                group_id=group.id,
            )
            session.add(expense)
            session.flush()

            for split in payload.splits:
                session.add(
                    ExpenseSplitRecord(
                        expense_id=expense.id,
                        member_id=split.member_id,
                        amount=split.amount,
                    )
                )

            session.commit()
            session.refresh(expense)
            return self._expense_record_to_schema(expense)

    def parse_receipt(self, receipt_text: str) -> ReceiptParseResponse:
        cleaned = receipt_text.strip()
        if not cleaned:
            raise ValueError('Paste a receipt text first.')

        total_match = None
        patterns = [
            r'(?:total|amount|paid|bill)[^\d]*(\d+(?:\.\d{1,2})?)',
            r'\$?\s?(\d+(?:\.\d{1,2})?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, cleaned, flags=re.IGNORECASE)
            if match:
                total_match = match.group(1)
                break

        amount = float(total_match) if total_match else 0.0

        description = 'Parsed receipt expense'
        for line in cleaned.splitlines():
            clean_line = line.strip()
            if not clean_line:
                continue
            if any(token in clean_line.lower() for token in ['total', 'amount', 'paid', 'bill', 'receipt']):
                continue
            description = clean_line
            break

        return ReceiptParseResponse(description=description, total_amount=amount)

    def _group_record_to_schema(self, group_record: GroupRecord) -> Group:
        return Group(
            id=group_record.id,
            name=group_record.name,
            members=[Member(id=member.id, name=member.name) for member in group_record.members],
            expenses=[self._expense_record_to_schema(expense) for expense in group_record.expenses],
        )

    def _expense_record_to_schema(self, expense_record: ExpenseRecord) -> Expense:
        return Expense(
            id=expense_record.id,
            description=expense_record.description,
            total_amount=expense_record.total_amount,
            payer_id=expense_record.payer_id,
            splits=[
                ExpenseSplit(member_id=split.member_id, amount=split.amount)
                for split in expense_record.splits
            ],
        )

    def _get_group_or_raise(self, session: Session, group_id: str) -> GroupRecord:
        group = session.get(GroupRecord, group_id)
        if group is None:
            raise ValueError('Group not found.')
        return group


class AppState:
    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or DEFAULT_DATABASE_URL
        self.engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False} if self.database_url.startswith('sqlite') else None,
            poolclass=StaticPool if self.database_url in {'sqlite://', 'sqlite:///:memory:'} else None,
        )
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False, autoflush=False)
        Base.metadata.create_all(self.engine)
        self.repository = DatabaseRepository(self.session_factory)
        self.repository.seed_default_data()


def create_app_state(database_url: str | None = None) -> AppState:
    return AppState(database_url=database_url)


app = FastAPI(title='AI Expense Splitter API', version='1.0.0')
app.state.app_state = create_app_state()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:4173',
        'http://127.0.0.1:4173',
        'http://0.0.0.0:4173',
    ],
    allow_origin_regex=r'https://.*\.app\.github\.dev',
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
def read_root() -> dict[str, str]:
    return {'message': 'AI Expense Splitter API'}


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    error = exc.errors()[0]
    message = error.get('msg', 'Invalid request.')
    return JSONResponse(status_code=400, content={'detail': message})


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={'detail': str(exc)})


@app.get('/api/groups')
def get_groups() -> list[Group]:
    return app.state.app_state.repository.get_groups()


@app.post('/api/groups', status_code=201)
def create_group(payload: CreateGroupRequest) -> Group:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail='Group name is required.')
    return app.state.app_state.repository.create_group(name)


@app.post('/api/groups/{group_id}/members', status_code=201)
def add_member(group_id: str, payload: CreateMemberRequest) -> Member:
    try:
        return app.state.app_state.repository.add_member(group_id, payload.name)
    except ValueError as exc:
        if str(exc) == 'Group not found.':
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post('/api/groups/{group_id}/expenses', status_code=201)
def create_expense(group_id: str, payload: CreateExpenseRequest) -> Expense:
    try:
        return app.state.app_state.repository.add_expense(group_id, payload)
    except ValueError as exc:
        if str(exc) == 'Group not found.':
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post('/api/ai/parse-receipt')
def parse_receipt(payload: ReceiptParseRequest) -> ReceiptParseResponse:
    try:
        return app.state.app_state.repository.parse_receipt(payload.receipt_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
