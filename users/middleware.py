def update_last_seen_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = get_response(request)

        if request.user.is_authenticated:
            request.user.save(update_fields=['last_seen'])

        return response

    return middleware