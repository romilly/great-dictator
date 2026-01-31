"""Custom PyHamcrest matchers for the test suite."""

from typing import Any

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description


class IsDocumentResponseMatcher(BaseMatcher[dict[str, Any]]):
    """Matcher for document API response with optional property checks."""

    def __init__(
        self,
        name: str | None = None,
        content: str | None = None,
        user: str | None = None,
        has_id: bool = False,
    ):
        self.expected_name = name
        self.expected_content = content
        self.expected_user = user
        self.check_has_id = has_id

    def _matches(self, item: dict[str, Any]) -> bool:
        if not isinstance(item, dict):
            return False
        if self.check_has_id and "id" not in item:
            return False
        if self.expected_name is not None and item.get("name") != self.expected_name:
            return False
        if self.expected_content is not None and item.get("content") != self.expected_content:
            return False
        if self.expected_user is not None and item.get("user") != self.expected_user:
            return False
        return True

    def describe_to(self, description: Description) -> None:
        parts = ["a document response"]
        if self.check_has_id:
            parts.append("with an id")
        if self.expected_name is not None:
            parts.append(f"with name={self.expected_name!r}")
        if self.expected_content is not None:
            parts.append(f"with content={self.expected_content!r}")
        if self.expected_user is not None:
            parts.append(f"with user={self.expected_user!r}")
        description.append_text(" ".join(parts))

    def describe_mismatch(
        self, item: dict[str, Any], mismatch_description: Description
    ) -> None:
        if not isinstance(item, dict):
            mismatch_description.append_text(f"was {type(item).__name__}")
        elif self.check_has_id and "id" not in item:
            mismatch_description.append_text("had no id")
        elif self.expected_name is not None and item.get("name") != self.expected_name:
            mismatch_description.append_text(f"had name={item.get('name')!r}")
        elif self.expected_content is not None and item.get("content") != self.expected_content:
            mismatch_description.append_text(f"had content={item.get('content')!r}")
        elif self.expected_user is not None and item.get("user") != self.expected_user:
            mismatch_description.append_text(f"had user={item.get('user')!r}")


def document_response(
    name: str | None = None,
    content: str | None = None,
    user: str | None = None,
    has_id: bool = False,
) -> IsDocumentResponseMatcher:
    """Match a document API response with optional property checks."""
    return IsDocumentResponseMatcher(name=name, content=content, user=user, has_id=has_id)


class IsResponseMatcher(BaseMatcher[Any]):
    """Matcher for HTTP response with status code and optional body matcher."""

    def __init__(
        self,
        status_code: int,
        body_matcher: Any | None = None,
    ):
        self.expected_status = status_code
        self.body_matcher = body_matcher

    def _matches(self, item: Any) -> bool:
        if not hasattr(item, "status_code"):
            return False
        if item.status_code != self.expected_status:
            return False
        if self.body_matcher is not None:
            return self.body_matcher.matches(item.json())
        return True

    def describe_to(self, description: Description) -> None:
        description.append_text(f"a response with status {self.expected_status}")
        if self.body_matcher is not None:
            description.append_text(" and body matching ")
            self.body_matcher.describe_to(description)

    def describe_mismatch(self, item: Any, mismatch_description: Description) -> None:
        if not hasattr(item, "status_code"):
            mismatch_description.append_text(f"was {type(item).__name__}")
        elif item.status_code != self.expected_status:
            mismatch_description.append_text(f"had status {item.status_code}")
        elif self.body_matcher is not None:
            mismatch_description.append_text("body ")
            self.body_matcher.describe_mismatch(item.json(), mismatch_description)


def is_ok_with(body_matcher: Any) -> IsResponseMatcher:
    """Match a 200 OK response with body matching the given matcher."""
    return IsResponseMatcher(200, body_matcher)


def is_created_with(body_matcher: Any) -> IsResponseMatcher:
    """Match a 201 Created response with body matching the given matcher."""
    return IsResponseMatcher(201, body_matcher)


def is_no_content() -> IsResponseMatcher:
    """Match a 204 No Content response."""
    return IsResponseMatcher(204)


def is_not_found() -> IsResponseMatcher:
    """Match a 404 Not Found response."""
    return IsResponseMatcher(404)
