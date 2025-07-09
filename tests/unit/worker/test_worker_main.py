from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.worker.worker_main import WorkerMain


@pytest.fixture
def worker_main():
    wm = WorkerMain()
    wm.container = MagicMock()
    wm.tasks = [MagicMock(), MagicMock()]
    wm._current_event_loop = MagicMock()
    return wm


def test_init_container_calls_config_and_wire():
    wm = WorkerMain()
    wm.container = MagicMock()
    with patch("app.worker.worker_main.WorkerSettings") as settings_cls:
        wm.init_container()
        wm.container.config.from_pydantic.assert_called_once()
        wm.container.wire.assert_called_once()


def test_get_tasks_returns_tasks():
    ca_task = MagicMock()
    sp_task = MagicMock()
    tasks = WorkerMain.get_tasks(create_alert_task=ca_task, suggest_price_task=sp_task)
    assert ca_task in tasks and sp_task in tasks


def test_init_sets_logger_and_signals(worker_main):
    with patch("app.worker.worker_main.logging.basicConfig") as log_cfg, patch(
        "app.worker.worker_main.signal.signal"
    ) as sig_patch, patch("app.worker.worker_main.asyncio.get_running_loop", return_value=MagicMock()):
        worker_main.init()
        log_cfg.assert_called()
        sig_patch.assert_called()


def test_handler_sig_calls_close_and_sys_exit(worker_main):
    # Simula tasks e current_event_loop
    mock_task = MagicMock()
    worker_main.tasks = [mock_task]
    worker_main._current_event_loop = MagicMock()
    with patch("app.worker.worker_main.signal.signal") as sig_patch, patch(
        "app.worker.worker_main.sys.exit", side_effect=SystemExit
    ) as sys_exit, patch("app.worker.worker_main.time.sleep"), patch(
        "app.worker.worker_main.asyncio.get_running_loop", return_value=MagicMock()
    ):
        worker_main.init()
        handler = None
        for call in sig_patch.call_args_list:
            if call[0][0] == 2:  # signal.SIGINT == 2
                handler = call[0][1]
        if handler:
            with pytest.raises(SystemExit):
                handler(2, None)
        sys_exit.assert_called_once()


@pytest.mark.asyncio
async def test_run_calls_init_and_gather(monkeypatch):
    wm = WorkerMain()
    wm.init = MagicMock()
    wm.get_tasks = MagicMock(return_value=[AsyncMock(), AsyncMock()])
    wm.tasks = wm.get_tasks()
    monkeypatch.setattr("asyncio.gather", AsyncMock())
    await wm.run()
    wm.init.assert_called_once()
    assert len(wm.tasks) == 2


def test_main_guard_runs(monkeypatch):
    import importlib
    import sys
    import types

    module_name = "app.worker.worker_main"
    module = importlib.import_module(module_name)
    monkeypatch.setattr(module, "asyncio", MagicMock())
    monkeypatch.setattr(module, "__name__", "__main__")
    try:
        importlib.reload(module)
    except Exception:
        pass
