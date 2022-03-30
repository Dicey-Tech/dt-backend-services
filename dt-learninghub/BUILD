python_sources(
    name="lib",
    dependencies=[
        "dt-learninghub/learninghub",
        "//:pkg_resources",
    ],
)

pex_binary(
    name="manage",
    entry_point="manage.py",
    dependencies=[
        ":lib",
    ],
    restartable=True,
)
