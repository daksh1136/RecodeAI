from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_supported_languages():
    response = client.get("/api/languages")

    assert response.status_code == 200

    languages = response.json()["languages"]

    assert "python" in languages
    assert "javascript" in languages
    assert "java" in languages


def test_python_security_analysis():
    code = """
import os

value = eval(input("Expression: "))
os.system(input("Command: "))

try:
    print(value)
except:
    print("error")
"""

    response = client.post(
        "/api/analyze",
        json={
            "code": code,
            "language": "python",
        },
    )

    assert response.status_code == 200

    data = response.json()

    titles = [finding["title"] for finding in data["findings"]]

    assert "Dynamic eval() usage" in titles
    assert "Shell command execution" in titles
    assert "Bare except block" in titles

    assert data["scores"]["security"] < 100
    assert len(data["modernization_plan"]) > 0


def test_javascript_legacy_analysis():
    code = """
function calculate(value) {
    var result = value;

    if (result == "10") {
        return result;
    }
}
"""

    response = client.post(
        "/api/analyze",
        json={
            "code": code,
            "language": "javascript",
        },
    )

    assert response.status_code == 200

    data = response.json()

    titles = [finding["title"] for finding in data["findings"]]

    assert "Legacy var declaration" in titles
    assert "Loose equality comparison" in titles


def test_javascript_safe_modernization():
    code = """
function greet(name) {
    var message = "Hello " + name;
    return message;
}
"""

    response = client.post(
        "/api/modernize",
        json={
            "code": code,
            "language": "javascript",
            "apply_safe_fixes": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "var message" in data["original_code"]
    assert "let message" in data["modernized_code"]
    assert data["original_code"] != data["modernized_code"]
    assert len(data["unified_diff"]) > 0


def test_java_legacy_analysis():
    code = """
import java.util.Vector;

public class Legacy {
    public static void main(String[] args) {
        Vector<String> users = new Vector<>();
        System.out.println(users);
    }
}
"""

    response = client.post(
        "/api/analyze",
        json={
            "code": code,
            "language": "java",
        },
    )

    assert response.status_code == 200

    data = response.json()

    titles = [finding["title"] for finding in data["findings"]]

    assert "Legacy Vector collection" in titles
    assert "Direct console output" in titles


def test_java_safe_modernization():
    code = """
Vector<String> users = new Vector<>();
Hashtable<String, String> config = new Hashtable<>();
"""

    response = client.post(
        "/api/modernize",
        json={
            "code": code,
            "language": "java",
            "apply_safe_fixes": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "ArrayList<String>" in data["modernized_code"]
    assert "HashMap<String, String>" in data["modernized_code"]


def test_unsupported_language():
    response = client.post(
        "/api/analyze",
        json={
            "code": "echo hello",
            "language": "cobol",
        },
    )

    assert response.status_code == 400


def test_empty_code_rejected():
    response = client.post(
        "/api/analyze",
        json={
            "code": "",
            "language": "python",
        },
    )

    assert response.status_code == 422
