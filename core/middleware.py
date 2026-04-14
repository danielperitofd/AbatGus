from organizations.models import Organization


class CurrentOrganizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.current_organization = None

        if request.user.is_authenticated:
            organization_id = request.session.get("current_organization_id")

            if request.user.organization_id and (
                not organization_id or not request.user.is_master_global
            ):
                organization_id = request.user.organization_id
                request.session["current_organization_id"] = organization_id

            if organization_id:
                request.current_organization = Organization.objects.filter(
                    pk=organization_id,
                    is_active=True,
                ).first()

        return self.get_response(request)
