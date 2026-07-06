"""Tests du parseur SQL."""

from __future__ import annotations

from payload_sentinel.sql_parser import extract_columns_from_sql


def test_extract_columns_from_quoted_select() -> None:
    sql = (
        'SELECT "auth_user"."id", "auth_user"."password", "auth_user"."email" '
        'FROM "auth_user" WHERE "auth_user"."id" = 1'
    )
    columns = extract_columns_from_sql(sql)
    names = [column.column for column in columns]
    assert "id" in names
    assert "password" in names
    assert "email" in names


def test_extract_columns_ignores_non_select() -> None:
    assert extract_columns_from_sql("INSERT INTO book (title) VALUES ('x')") == ()


def test_extract_columns_handles_wildcard() -> None:
    columns = extract_columns_from_sql('SELECT * FROM "book"')
    assert len(columns) == 1
    assert columns[0].wildcard is True
