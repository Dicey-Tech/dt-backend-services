python_sources(
    name="lib",
    dependencies=[
        "dt-learninghub/learninghub/settings",
        "dt-learninghub/learninghub/apps/classrooms",
    ]
)

pex_binary(
    name="manage",
    entry_point="manage.py",
        dependencies=[
        ":lib"
    ],
    restartable=True,
)

python_requirements(
    source="requirements/dev.txt",
    module_mapping={
        "edx-drf-extensions" : ["edx_rest_framework_extensions"]
    },
)

python_requirements()
