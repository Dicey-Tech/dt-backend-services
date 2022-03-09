"""
Rules needed to restrict access to the classroom management service.
"""
import logging

import crum
import rules
from edx_rbac.utils import (
    get_decoded_jwt,
    request_user_has_implicit_access_via_jwt,
    user_has_access_via_database,
)
from learninghub.apps.classrooms import constants
from learninghub.apps.classrooms.models import ClassroomRoleAssignment

logger = logging.getLogger(__name__)


def current_decoded_jwt():
    return get_decoded_jwt(crum.get_current_request())


@rules.predicate
def has_implicit_access_to_classroom_admin(
    user, school_uuid
):  # pylint: disable=unused-argument
    """
    Check that if request has implicit access to the given enterprise UUID
    for the `CLASSROOM` feature role.

    Returns:
        boolean: whether the request user has access.
    """

    if not school_uuid:
        return False

    return request_user_has_implicit_access_via_jwt(
        current_decoded_jwt(),
        constants.CLASSROOM_TEACHER_ROLE,
        str(school_uuid),
    )


@rules.predicate
def has_explicit_access_to_classroom_admin(user, school_uuid):
    """
    Check that if request user has explicit access to `SUBSCRIPTIONS_ADMIN_ROLE` feature role.
    Returns:
        boolean: whether the request user has access.
    """
    if not school_uuid:
        return False

    return user_has_access_via_database(
        user,
        constants.CLASSROOM_TEACHER_ROLE,
        ClassroomRoleAssignment,
        str(school_uuid),
    )


has_teacher_access = (
    has_implicit_access_to_classroom_admin | has_explicit_access_to_classroom_admin
)
rules.add_perm(constants.CLASSROOM_TEACHER_ACCESS_PERMISSION, has_teacher_access)
