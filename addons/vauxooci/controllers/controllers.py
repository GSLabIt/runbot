# -*- coding: utf-8 -*-
import json
import requests

from openerp import http
from openerp.http import request


def s2human(time):
    """Convert a time in second into an human readable string"""
    for delay, desc in [(86400,'d'),(3600,'h'),(60,'m')]:
        if time >= delay:
            return str(int(time / delay)) + desc
    return str(int(time)) + "s"


class RunbotButtons(http.Controller):

    def build_info(self, build):
        real_build = build.duplicate_id if build.state == 'duplicate' else build
        return {
            'id': build.id,
            'name': build.name,
            'state': real_build.state,
            'result': real_build.result,
            'subject': build.subject,
            'author': build.author,
            'committer': build.committer,
            'dest': build.dest,
            'real_dest': real_build.dest,
            'job_age': s2human(real_build.job_age),
            'job_time': s2human(real_build.job_time),
            'job': real_build.job,
            'domain': real_build.domain,
            'host': real_build.host,
            'port': real_build.port,
            'subject': build.subject,
            'server_match': real_build.server_match,
        }

    def build_html(self, build):
        res = []
        try:
            url = 'http://%s/instance_introspection.json' % build.domain
            response = requests.get(url,
                                    timeout=5.00)
            if response.status_code == requests.codes.ok:
                res = response.json()
        except requests.exceptions.Timeout:
            res = [{'info': {'error': 'Timeout',
                 'message': '''Instance is not running
https://github.com/Vauxoo/server-tools/tree/8.0/instance_introspection
read the help to know how configure it properlly'''}}]
        except requests.exceptions.TooManyRedirects:
            res = [{'info': {'error': 'TooMany redirect',
                 'message': '''Install properly the instance_introspection:
https://github.com/Vauxoo/server-tools/tree/8.0/instance_introspection
read the help to know how'''}}]
        except requests.exceptions.RequestException as e:
            res = [{'info': {'error': 'Unknown Error',
                 'message': '''%s''' % e.message}}]
            # catastrophic error. bail.
            _logger.log(e)
        return res

    @http.route(['/vauxooci/build_button/<build_id>'], type='http', auth="public", website=True)
    def build(self, build_id=None, search=None, **post):
        registry, cr, uid, context = request.registry, request.cr, request.uid, request.context

        Build = registry['runbot.build']

        build = Build.browse(cr, uid, [int(build_id)])[0]
        if not build.exists():
            return request.not_found()
        context = {
            'introspection': build.introspection,
            'introspection_html': self.build_html(build),
            'repo': build.repo_id,
            'bu': self.build_info(build),
            'br': {'branch': build.branch_id},
        }
        return request.render("vauxooci.build_button", context)

#     @http.route('/runbot_frontend/runbot_frontend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('runbot_frontend.listing', {
#             'root': '/runbot_frontend/runbot_frontend',
#             'objects': http.request.env['runbot_frontend.runbot_frontend'].search([]),
#         })

#     @http.route('/runbot_frontend/runbot_frontend/objects/<model("runbot_frontend.runbot_frontend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('runbot_frontend.object', {
#             'object': obj
#         })
