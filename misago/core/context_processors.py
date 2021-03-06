def site_address(request):
    if request.is_secure():
        site_protocol = 'https'
        address_template = 'https://%s'
    else:
        site_protocol = 'http'
        address_template = 'http://%s'

    host = request.get_host()

    return {
        'SITE_PROTOCOL': site_protocol,
        'SITE_HOST': host,
        'SITE_ADDRESS': address_template % host
    }


def frontend_context(request):
    return {'frontend_context': request.frontend_context}
