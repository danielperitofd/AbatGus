from threading import local


_runtime = local()


def set_current_organization(organization):
    _runtime.current_organization = organization


def get_current_organization():
    return getattr(_runtime, "current_organization", None)
