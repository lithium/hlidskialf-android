import jinja2
import os
import mimetypes

TOP_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIRS = [
    os.path.join(TOP_DIR, 'templates'),
]
STATIC_ROOT = os.path.join(TOP_DIR, 'static')



def application(environ, start_response):
    def redirect_to(url):
        start_response("301 Moved Permanently", [("Location", url)])
        return [""]

    def render_template(names, status='200 OK'):
        try:
            template = jinja_env.select_template(names)
            data = str(template.render(context))
            return (status, data)
        except (jinja2.TemplateNotFound, IOError) as e:
            return (None, None)




    # load data from environment
    path = environ.get('PATH_INFO', '/')
    context = {
        'STATIC_URL': '/static/',
        'path': path,
    }


    data = None
    status = None
    headers = {
        'Content-Type': 'text/html',
    }


    # serve static files for debug purposes
    if path.startswith(context['STATIC_URL']) or path == '/favicon.ico':
        path = path.replace(context['STATIC_URL'],'').lstrip('/')
        try:

            with open(os.path.join(STATIC_ROOT, path), 'rb') as fh:
                headers['Content-Type'] = mimetypes.guess_type(path)[0]
                status = '200 OK'
                data = str(fh.read())
        except IOError:
            status = '404 Not Found'
            data = ""

    else:
        # render the jinja template
        try:
            # initialize jinja2 
            jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIRS))

            #determine filename from path
            if path == '/':
                names = ['index.html']
            elif path.endswith('/'):
                return redirect_to(path.rstrip('/'))
            elif path.endswith('.html'):
                return redirect_to(path.rstrip('.html'))
            else:
                names = [path+'.html', path+'/index.html']

            status, data = render_template(names)

            # 404 occurred
            if status is None: 
                status, data = render_template(['404.html','errors/404.html'], status='404 Not Found')
                if status is None:
                    data = """<h1>404 Not Found</h1><pre>%s</pre>""" % (names,)
                    status = '404 Not Found'

        except Exception as e:
            # any exception we just treat as a 500.
            status, data = render_template(['500.html','errors/500.html'], status='500 Internal Error')
            if status is None:
                data = """<h1>500 Internal Error</h1><pre>%s</pre>""" % (e,)
                status = '500 Internal Error'

    headers['Content-Length'] = str(len(data))
    start_response(status, headers.items())
    return [data]
