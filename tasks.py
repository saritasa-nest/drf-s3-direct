import invoke
import saritasa_invocations

ns = invoke.Collection(
    saritasa_invocations.git,
    saritasa_invocations.pre_commit,
    saritasa_invocations.system,
    saritasa_invocations.poetry,
    saritasa_invocations.mypy,
    saritasa_invocations.pytest,
)

# Configurations for run command
ns.configure(
    dict(
        run=dict(
            pty=True,
            echo=True,
        ),
    ),
)
