"""食譜查詢條件組裝的測試。

只測純邏輯（把前端條件轉成查詢參數、把查詢參數組成 ORM 的 Q 物件），
不需要 torch / transformers，也不需要匯入真實食譜資料。

`__process_UserQuery` 與 `__query_set` 是 name-mangled 的內部方法，
測試以 `_DB_search__xxx` 存取，因為它們是這個模組真正的核心邏輯。
"""
import pytest

from recipe.DB_query import DB_search


@pytest.fixture
def searcher():
    return DB_search()


def process(searcher, data, user_query):
    return searcher._DB_search__process_UserQuery(data, user_query)


def build_query(searcher, data):
    return searcher._DB_search__query_set(data)


def empty_data():
    return {"object": {}, "Attribute": {}}


# ---------------------------------------------------------------------------
# 前端條件 -> 查詢參數
# ---------------------------------------------------------------------------

class TestUserQueryProcessing:
    def test_empty_user_query_is_passed_through(self, searcher):
        data = {"object": {"ingredients": ["chicken"]}, "Attribute": {}}
        assert process(searcher, data, []) is data

    def test_tag_is_appended_to_object_tags(self, searcher):
        res = process(searcher, empty_data(), ["japanese"])
        assert res["object"]["tags"] == ["japanese"]

    def test_time_option_becomes_minutes_upper_bound(self, searcher):
        res = process(searcher, empty_data(), ["30-minutes-or-less"])
        assert res["Attribute"]["minutes"] == 30

    def test_time_to_make_becomes_minutes_lower_bound(self, searcher):
        res = process(searcher, empty_data(), ["time-to-make"])
        assert res["Attribute"]["minutes_up"] == 60

    def test_health_option_is_translated_by_the_rule_engine(self, searcher):
        """alcohol-free 經規則轉換後應寫進 tags 為 non-alcoholic。

        原本在 tags 尚未建立時會 KeyError（500），這裡固定住修正後的行為。
        """
        res = process(searcher, empty_data(), ["alcohol-free"])
        assert res["object"]["tags"] == ["non-alcoholic"]

    def test_health_option_does_not_duplicate_existing_tag(self, searcher):
        data = {"object": {"tags": ["non-alcoholic"]}, "Attribute": {}}
        res = process(searcher, data, ["alcohol-free"])
        assert res["object"]["tags"] == ["non-alcoholic"]

    def test_unknown_option_is_ignored(self, searcher):
        res = process(searcher, empty_data(), ["not-a-real-option"])
        assert res["object"] == {}
        assert res["Attribute"] == {}

    def test_multiple_options_combine(self, searcher):
        res = process(searcher, empty_data(),
                      ["japanese", "15-minutes-or-less", "high-protein"])
        assert set(res["object"]["tags"]) == {"japanese", "high-protein"}
        assert res["Attribute"]["minutes"] == 15


# ---------------------------------------------------------------------------
# 查詢參數 -> ORM Q 物件
# ---------------------------------------------------------------------------

class TestQuerySetBuilding:
    def test_empty_data_builds_empty_queries(self, searcher):
        query_a, query_b = build_query(searcher, empty_data())
        assert len(query_a) == 0
        assert len(query_b) == 0

    def test_object_fields_use_icontains(self, searcher):
        query_a, _ = build_query(
            searcher, {"object": {"name": "curry", "ingredients": "chicken"}})
        rendered = str(query_a)
        assert "name__icontains" in rendered
        assert "ingredients__icontains" in rendered

    def test_minutes_becomes_upper_bound(self, searcher):
        _, query_b = build_query(searcher, {"Attribute": {"minutes": 30}})
        assert "minutes__lte" in str(query_b)

    def test_minutes_up_becomes_lower_bound(self, searcher):
        _, query_b = build_query(searcher, {"Attribute": {"minutes_up": 60}})
        assert "minutes__gt" in str(query_b)

    def test_nutrition_limits_are_upper_bounds(self, searcher):
        _, query_b = build_query(searcher, {"Attribute": {
            "calories": 500, "fat": 20, "sodium": 800, "protein": 30}})
        rendered = str(query_b)
        for field in ("calories__lte", "fat__lte", "sodium__lte",
                      "protein__lte"):
            assert field in rendered

    def test_conditions_are_combined_with_and(self, searcher):
        _, query_b = build_query(
            searcher, {"Attribute": {"calories": 500, "n_steps": 8}})
        assert query_b.connector == "AND"
        assert len(query_b) == 2
