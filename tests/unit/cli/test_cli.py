from typer.testing import CliRunner

from app.cli import app


def test_doctor_command_outputs_status():
    runner = CliRunner()

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "应用环境检查" in result.stdout
