"""Tests for PageIterator."""

from unittest.mock import MagicMock, call

from satnogs_network_api.models import Observation
from satnogs_network_api.pagination import PageIterator

from tests.conftest import SAMPLE_OBSERVATION, make_paginated_response, mock_response


class TestPageIterator:
    def _make_iterator(self, session, url="https://example.com/api/", params=None):
        return PageIterator(
            session=session,
            url=url,
            params=params or {},
            model=Observation,
        )

    def test_single_page(self):
        session = MagicMock()
        data = make_paginated_response([SAMPLE_OBSERVATION])
        session.get.return_value = mock_response(data)

        it = self._make_iterator(session)
        results = list(it)

        assert len(results) == 1
        assert isinstance(results[0], Observation)
        assert results[0].id == 1001

    def test_multiple_pages(self):
        session = MagicMock()
        obs1 = {**SAMPLE_OBSERVATION, "id": 1}
        obs2 = {**SAMPLE_OBSERVATION, "id": 2}

        page1 = make_paginated_response([obs1], next_url="https://example.com/api/?cursor=abc")
        page2 = make_paginated_response([obs2])

        session.get.side_effect = [
            mock_response(page1),
            mock_response(page2),
        ]

        it = self._make_iterator(session)
        results = list(it)

        assert len(results) == 2
        assert results[0].id == 1
        assert results[1].id == 2
        assert session.get.call_count == 2

    def test_empty_results(self):
        session = MagicMock()
        data = make_paginated_response([])
        session.get.return_value = mock_response(data)

        it = self._make_iterator(session)
        results = list(it)

        assert results == []

    def test_list_response_format(self):
        """Some endpoints return a plain list instead of paginated dict."""
        session = MagicMock()
        session.get.return_value = mock_response([SAMPLE_OBSERVATION])

        it = self._make_iterator(session)
        results = list(it)

        assert len(results) == 1
        assert results[0].id == 1001

    def test_lazy_fetching(self):
        """Pages are only fetched when iterated."""
        session = MagicMock()
        obs1 = {**SAMPLE_OBSERVATION, "id": 1}
        obs2 = {**SAMPLE_OBSERVATION, "id": 2}

        page1 = make_paginated_response([obs1], next_url="https://example.com/api/?cursor=abc")
        page2 = make_paginated_response([obs2])

        session.get.side_effect = [
            mock_response(page1),
            mock_response(page2),
        ]

        it = self._make_iterator(session)
        # No fetch yet
        assert session.get.call_count == 0

        # First next() triggers first page fetch
        first = next(it)
        assert first.id == 1
        assert session.get.call_count == 1

    def test_early_termination(self):
        """Breaking out of iteration doesn't fetch remaining pages."""
        session = MagicMock()
        obs1 = {**SAMPLE_OBSERVATION, "id": 1}

        page1 = make_paginated_response([obs1], next_url="https://example.com/api/?cursor=abc")
        session.get.return_value = mock_response(page1)

        it = self._make_iterator(session)
        first = next(it)
        assert first.id == 1
        # Only one page fetched despite next_url existing
        assert session.get.call_count == 1

    def test_params_passed_on_first_request(self):
        session = MagicMock()
        data = make_paginated_response([])
        session.get.return_value = mock_response(data)

        params = {"status": "good", "norad_cat_id": 25544}
        it = self._make_iterator(session, params=params)
        list(it)

        session.get.assert_called_once_with(
            "https://example.com/api/",
            params=params,
        )

    def test_next_url_used_directly(self):
        """Subsequent pages use the next URL directly, not the original params."""
        session = MagicMock()
        obs1 = {**SAMPLE_OBSERVATION, "id": 1}
        obs2 = {**SAMPLE_OBSERVATION, "id": 2}

        next_url = "https://example.com/api/?cursor=abc123"
        page1 = make_paginated_response([obs1], next_url=next_url)
        page2 = make_paginated_response([obs2])

        session.get.side_effect = [
            mock_response(page1),
            mock_response(page2),
        ]

        it = self._make_iterator(session, params={"status": "good"})
        list(it)

        assert session.get.call_count == 2
        # Second call uses the next URL with no params
        session.get.assert_called_with(next_url, params=None)

    def test_stopiteration_on_exhausted(self):
        session = MagicMock()
        data = make_paginated_response([SAMPLE_OBSERVATION])
        session.get.return_value = mock_response(data)

        it = self._make_iterator(session)
        next(it)

        try:
            next(it)
            assert False, "Should have raised StopIteration"
        except StopIteration:
            pass


class TestPageIteratorJsonMode:
    def test_json_returns_dicts(self):
        session = MagicMock()
        data = make_paginated_response([SAMPLE_OBSERVATION])
        session.get.return_value = mock_response(data)

        it = PageIterator(
            session=session,
            url="https://example.com/api/",
            params={},
            model=Observation,
        )

        results = list(it.json())
        assert len(results) == 1
        assert isinstance(results[0], dict)
        assert results[0]["id"] == 1001

    def test_json_does_not_affect_original(self):
        session = MagicMock()
        data = make_paginated_response([SAMPLE_OBSERVATION])
        session.get.side_effect = [
            mock_response(data),
            mock_response(make_paginated_response([SAMPLE_OBSERVATION])),
        ]

        it = PageIterator(
            session=session,
            url="https://example.com/api/",
            params={},
            model=Observation,
        )

        # .json() returns a new iterator
        json_it = it.json()
        assert json_it is not it

    def test_json_multi_page(self):
        session = MagicMock()
        obs1 = {**SAMPLE_OBSERVATION, "id": 1}
        obs2 = {**SAMPLE_OBSERVATION, "id": 2}

        page1 = make_paginated_response([obs1], next_url="https://example.com/api/?cursor=x")
        page2 = make_paginated_response([obs2])

        session.get.side_effect = [
            mock_response(page1),
            mock_response(page2),
        ]

        it = PageIterator(
            session=session,
            url="https://example.com/api/",
            params={},
            model=Observation,
        ).json()

        results = list(it)
        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[1]["id"] == 2
