from blsetup.domain import InstallCommand, InstallState, InstallWorkflow, InvalidTransition


def test_happy_path_and_progress_events():
    workflow = InstallWorkflow()
    assert workflow.state is InstallState.CHECKING
    for command in (
        InstallCommand.CHECK_OK,
        InstallCommand.MANIFEST_OK,
        InstallCommand.PREPARED,
    ):
        workflow.dispatch(command)
    assert workflow.dispatch(InstallCommand.DOWNLOAD_PROGRESS, progress=42).progress == 42
    for command in (
        InstallCommand.DOWNLOAD_OK,
        InstallCommand.VERIFY_OK,
        InstallCommand.INSTALL_OK,
    ):
        workflow.dispatch(command)
    assert workflow.state is InstallState.COMPLETED
    assert workflow.terminal


def test_cancel_is_terminal_and_invalid_commands_are_rejected():
    workflow = InstallWorkflow()
    event = workflow.dispatch(InstallCommand.CANCEL)
    assert event.state is InstallState.CANCELLED
    try:
        workflow.dispatch(InstallCommand.RETRY)
    except InvalidTransition:
        pass
    else:
        raise AssertionError("terminal workflow accepted a command")


def test_failure_can_enter_rollback_then_failed():
    workflow = InstallWorkflow()
    for command in (
        InstallCommand.CHECK_OK,
        InstallCommand.MANIFEST_OK,
        InstallCommand.PREPARED,
        InstallCommand.DOWNLOAD_OK,
        InstallCommand.VERIFY_OK,
    ):
        workflow.dispatch(command)
    failure = workflow.dispatch(InstallCommand.FAIL, rollback=True, error_id="install-1")
    assert failure.state is InstallState.ROLLING_BACK
    assert workflow.dispatch(InstallCommand.ROLLBACK_OK).state is InstallState.FAILED
    assert workflow.dispatch(InstallCommand.RETRY).state is InstallState.CHECKING
