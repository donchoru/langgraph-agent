"""Jinja2 SQL 템플릿 엔진."""
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent.parent / "templates"),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_sql(template_name: str, **params) -> tuple[str, dict]:
    """SQL 템플릿을 렌더링하여 (SQL, 바인딩 파라미터) 튜플 반환.

    Jinja2는 SQL 구조(WHERE, JOIN)를 제어하고,
    값은 :named_param 바인딩으로 전달하여 SQL Injection 방지.
    """
    template = _env.get_template(template_name)
    sql = template.render(**params)
    # None/빈 문자열인 파라미터는 바인딩에서 제외
    bind_params = {k: v for k, v in params.items() if v is not None and v != ""}
    return sql, bind_params
