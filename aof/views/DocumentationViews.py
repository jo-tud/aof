from functools import wraps
import os
from pyramid.httpexceptions import HTTPNotFound
from pyramid.path import AssetResolver
from pyramid.response import FileResponse
from pyramid.view import view_config
from aof.views.PageViews import PageViews
import logging

__author__ = 'khoerfurter'
log = logging.getLogger(__name__)

class DocumentExistsDecorator(object):
    """
    Decorator function:
    - Is there an document which matches the supplied URI

    # Use this only for subclasse of DocumentationViews
    """

    def __call__(self, f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if (issubclass(type(self), DocumentationViews)):
                document = self.request.matchdict['document']
                doc_path = os.path.join(self.docs_path, document)
                if os.path.exists(doc_path):
                    return f(self, *args, **kwargs)
                else:
                    return HTTPNotFound('The resource "%s" could not be found within the Documentation.' % document)
            else:
                import inspect

                log.info(
                    "DocumentExistsDecorator is used for a method ({}) which doesn't belong to the Documentation-Context!".format(
                        inspect.stack()[1][3]))
                return HTTPNotFound('The Documentation-Page could not be opened.')

        return wrapper

class DocumentationViews(PageViews):
    def __init__(self, context, request):
        """
        Class with all Documentation-Pages and -Actions
        """
        super(DocumentationViews, self).__init__(context, request)

        if request.registry is not None:
            self.docs_path = request.registry.settings['documentation_docs_path']
        else:
            self.docs_path = "aof:resources/docs"

        self.docs_path = AssetResolver().resolve(self.docs_path).abspath()

    @view_config(route_name='documentation', renderer='aof:templates/documentation.mako')
    def page_overview(self):
        """
        Documentation-Homepage with indexes the docs-path and shows all the accessible-files (HTML,LINK,PDF)
        :return: dictionary
        """
        self._setTitle('Documentation')

        def recursive_folder_dict(basepath, root):
            structure = list()
            allowed_doc_types = ('HTML', 'PDF', 'LINK')
            for file in os.listdir(basepath):
                if os.path.isdir(os.path.join(basepath, file)):
                    structure.append(
                        {"name": file, "children": recursive_folder_dict(os.path.join(basepath, file), root)})
                else:
                    tmp_name = os.path.splitext(file)
                    key = tmp_name[1].replace(".", "", 1).upper()
                    if key in allowed_doc_types:
                        if key == "LINK":
                            path = open(os.path.join(basepath, file)).read()
                        else:
                            if key == "HTML":
                                path = "/docs/"
                            else:
                                path = "/resources/"
                            path += os.path.join(basepath, file).replace(root+os.sep, "").replace(os.sep, "/")
                        for idx, s in enumerate(structure):
                            if s["name"] == tmp_name[0]:
                                s['resources'].update({key: path})
                                structure[idx] = s
                                break
                        else:
                            structure.append({"name": tmp_name[0], "children": None, 'resources': {key: path}})
            return structure

        basepath = self.docs_path
        structure = recursive_folder_dict(basepath, basepath)

        custom_args = {'structure': structure}
        return self._returnCustomDict(custom_args)

    @view_config(route_name='documentation-docs', renderer='aof:templates/documentation-docs.mako')
    @DocumentExistsDecorator()
    def page_html_view(self):
        """
        Shows a specific Documentation-document in HTML
        :return: dictionary
        """
        self._setTitle('Documentation')
        document = self.request.matchdict['document']
        content = open(os.path.join(self.docs_path, self.request.matchdict['document'])).read()

        custom_args = {'content': content}
        return self._returnCustomDict(custom_args)

    @view_config(route_name='documentation-resource')
    @DocumentExistsDecorator()
    def page_resource_response(self):
        """
        Shows a specific Documentation-document in PDF or other downloadable Mime-types
        :return: FileResponse with the document
        """
        document = self.request.matchdict['document']
        response = FileResponse(
            os.path.join(self.docs_path, document),
            request=self.request
        )
        return response

