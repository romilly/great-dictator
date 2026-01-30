import sqlite3
from datetime import datetime

import pytest
from hamcrest import assert_that, equal_to, is_, is_not

from great_dictator.domain.document import Document


def test_save_assigns_id_to_new_document(db_repository):
    doc = Document(
        user="romilly",
        name="test doc",
        content="hello world",
        created=datetime(2024, 1, 15, 10, 30),
    )

    saved = db_repository.save(doc)

    assert_that(saved.id, is_not(None))
    assert_that(saved.user, equal_to("romilly"))
    assert_that(saved.name, equal_to("test doc"))
    assert_that(saved.content, equal_to("hello world"))


def test_load_returns_none_for_missing_document(db_repository):
    result = db_repository.load(999)

    assert_that(result, is_(None))


def test_load_returns_saved_document(db_repository):
    doc = Document(
        user="romilly",
        name="test doc",
        content="hello world",
        created=datetime(2024, 1, 15, 10, 30),
    )
    saved = db_repository.save(doc)

    loaded = db_repository.load(saved.id)  # type: ignore[arg-type]

    assert_that(loaded, is_not(None))
    assert_that(loaded.id, equal_to(saved.id))  # type: ignore[union-attr]
    assert_that(loaded.user, equal_to("romilly"))  # type: ignore[union-attr]
    assert_that(loaded.name, equal_to("test doc"))  # type: ignore[union-attr]
    assert_that(loaded.content, equal_to("hello world"))  # type: ignore[union-attr]
    assert_that(loaded.created, equal_to(datetime(2024, 1, 15, 10, 30)))  # type: ignore[union-attr]


def test_save_updates_existing_document(db_repository):
    doc = Document(
        user="romilly",
        name="test doc",
        content="original content",
        created=datetime(2024, 1, 15, 10, 30),
    )
    saved = db_repository.save(doc)

    updated = Document(
        id=saved.id,
        user="romilly",
        name="test doc",
        content="updated content",
        created=datetime(2024, 1, 15, 10, 30),
    )
    db_repository.save(updated)

    loaded = db_repository.load(saved.id)  # type: ignore[arg-type]
    assert_that(loaded.content, equal_to("updated content"))  # type: ignore[union-attr]


def test_list_for_user_returns_only_users_documents(db_repository):
    doc1 = Document(
        user="romilly",
        name="doc1",
        content="content1",
        created=datetime(2024, 1, 15, 10, 30),
    )
    doc2 = Document(
        user="romilly",
        name="doc2",
        content="content2",
        created=datetime(2024, 1, 16, 11, 0),
    )
    doc3 = Document(
        user="other_user",
        name="doc3",
        content="content3",
        created=datetime(2024, 1, 17, 12, 0),
    )
    db_repository.save(doc1)
    db_repository.save(doc2)
    db_repository.save(doc3)

    result = db_repository.list_for_user("romilly")

    assert_that(len(result), equal_to(2))
    names = [s.name for s in result]
    assert "doc1" in names
    assert "doc2" in names


def test_delete_removes_document(db_repository):
    doc = Document(
        user="romilly",
        name="test doc",
        content="hello world",
        created=datetime(2024, 1, 15, 10, 30),
    )
    saved = db_repository.save(doc)

    result = db_repository.delete(saved.id)  # type: ignore[arg-type]

    assert_that(result, is_(True))
    assert_that(db_repository.load(saved.id), is_(None))  # type: ignore[arg-type]


def test_delete_returns_false_for_missing_document(db_repository):
    result = db_repository.delete(999)

    assert_that(result, is_(False))


def test_unique_constraint_on_user_and_name(db_repository):
    doc1 = Document(
        user="romilly",
        name="same name",
        content="content1",
        created=datetime(2024, 1, 15, 10, 30),
    )
    db_repository.save(doc1)

    doc2 = Document(
        user="romilly",
        name="same name",
        content="content2",
        created=datetime(2024, 1, 16, 11, 0),
    )

    with pytest.raises(sqlite3.IntegrityError):
        db_repository.save(doc2)
