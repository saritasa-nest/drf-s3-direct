import invoke
import saritasa_invocations

ns = invoke.Collection(
    saritasa_invocations.git,
    saritasa_invocations.pre_commit,
    saritasa_invocations.system,
    saritasa_invocations.poetry,
    saritasa_invocations.mypy,
    saritasa_invocations.pytest,
    saritasa_invocations.docker,
    saritasa_invocations.django,
)


@invoke.task
def prepare_ci_env(context: invoke.Context) -> None:
    """Prepare env for ci."""
    saritasa_invocations.docker.up(context)
    saritasa_invocations.github_actions.set_up_hosts(context)
    with context.cd("tests"):
        saritasa_invocations.django.wait_for_database(context)


ns.add_task(prepare_ci_env)  # type: ignore

# Configurations for run command
ns.configure(
    {
        "run": {
            "pty": True,
            "echo": True,
        },
        "saritasa_invocations": saritasa_invocations.Config(
            docker=saritasa_invocations.DockerSettings(
                main_containers=(
                    "postgres",
                    "minio",
                    "createbucket",
                ),
            ),
        ),
    },
)
