python_sources(
    name="lib",
    dependencies=[
        "dt-learninghub/learninghub",
    ],
)

pex_binary(
    name="manage",
    entry_point="manage.py",
    dependencies=[
        ":lib",
        "//:edx-django-release-util",
        "//:setuptools",
    ],
)
