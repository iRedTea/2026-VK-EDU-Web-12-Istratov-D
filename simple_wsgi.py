def simple_app(environ, start_response):
    method = environ.get('REQUEST_METHOD', 'GET')
    query = environ.get('QUERY_STRING', '')
    content_length = environ.get('CONTENT_LENGTH')
    body = b''
    if content_length:
        try:
            length = int(content_length)
            body = environ['wsgi.input'].read(length)
        except (ValueError, KeyError):
            body = b''

    params = []
    if query:
        params.append(f'GET: {query}')
    if body:
        params.append(f'POST: {body.decode("utf-8", errors="replace")}')

    response_body = 'Received parameters:\n' + '\n'.join(params)
    response_body = response_body.encode('utf-8')

    status = '200 OK'
    headers = [
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('Content-Length', str(len(response_body)))
    ]
    start_response(status, headers)
    return [response_body]
