"""Tests for the code-language classifier."""
from __future__ import annotations

from pdf2md.code_language import detect_language, tag_bare_fences

JAVA = """\
package com.manning.apisecurityinaction;
import org.dalesbred.Database;
public class Main {
  public static void main(String... args) throws Exception {
    var database = Database.forDataSource(datasource);
  }
}"""

SQL = """\
CREATE TABLE spaces(
  space_id INT PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);"""

BASH = "mvn clean compile exec:java"

XML = """\
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <dependency>
    <groupId>com.h2database</groupId>
  </dependency>
</project>"""

JSON = """\
{
  "error": "internal server error"
}"""

YAML = """\
apiVersion: v1
kind: Secret
metadata:
  name: db-password"""

PYTHON = """\
def authenticate(request):
    if request.user is None:
        print("no user")
    return None"""

HTTP = """\
GET /spaces/1 HTTP/1.1
Host: example.com"""


class TestDetectLanguage:
    def test_java(self) -> None:
        assert detect_language(JAVA) == "java"

    def test_sql(self) -> None:
        assert detect_language(SQL) == "sql"

    def test_bash(self) -> None:
        assert detect_language(BASH) == "bash"

    def test_xml(self) -> None:
        assert detect_language(XML) == "xml"

    def test_json(self) -> None:
        assert detect_language(JSON) == "json"

    def test_yaml(self) -> None:
        assert detect_language(YAML) == "yaml"

    def test_python(self) -> None:
        assert detect_language(PYTHON) == "python"

    def test_http(self) -> None:
        assert detect_language(HTTP) == "http"

    def test_java_fragment_ending_in_brace_is_not_json(self) -> None:
        # A continuation fragment of a Java listing: weak braces must not win.
        java_fragment = (
            "    var path = Paths.get(\n"
            '        Main.class.getResource("/schema.sql").toURI());\n'
            "    database.update(Files.readString(path));\n"
            "  }\n"
            "}"
        )
        assert detect_language(java_fragment) == "java"

    def test_unknown_returns_default(self) -> None:
        assert detect_language("just some prose words", default="java") == "java"

    def test_unknown_returns_none_without_default(self) -> None:
        assert detect_language("just some prose words") is None

    def test_empty_returns_default(self) -> None:
        assert detect_language("   ", default="java") == "java"


class TestTagBareFences:
    def test_tags_a_bare_fence(self) -> None:
        md = f"Here:\n\n```\n{SQL}\n```\n\nDone."
        out = tag_bare_fences(md)
        assert "```sql" in out

    def test_uses_default_for_unrecognized_block(self) -> None:
        md = "```\nhello world prose\n```"
        out = tag_bare_fences(md, default="text")
        assert out.startswith("```text\n")

    def test_leaves_already_tagged_fence_untouched(self) -> None:
        md = "```python\nprint('hi')\n```"
        assert tag_bare_fences(md) == md

    def test_no_change_when_unknown_and_no_default(self) -> None:
        md = "```\nhello world prose\n```"
        assert tag_bare_fences(md) == md
