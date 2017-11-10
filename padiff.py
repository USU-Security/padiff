import pan.xapi
import xmltodict


class PAFoo(object):
    # Do some stuff with a Palo Alto firewall while abstracting away as much
    # XML as possible.
    #
    # NB: this is not thread-safe

    def __init__(self, xpath, tag='usu-logan-a'):
        self.xapi = pan.xapi.PanXapi(tag=tag)
        self.xpath = xpath

    def _get_result(self):
        result = xmltodict.parse(self.xapi.xml_document)
        # FIXME: what should we do on an error?
        assert result['response']['@status'] == 'success'
        # FIXME: check @code?
        if result['response']['result'] is None:
            raise Exception("No result")
        return result

    def get_candidate(self, xpath=None):
        self.xapi.get(xpath)
        candidate = self._get_result()
        return candidate['response']['result']['entry']

    def get_active(self, xpath=None):
        self.xapi.show(xpath)
        active = self._get_result()
        return active['response']['result']['entry']

    def get_changes(self, user=None, ):
        cmd = ["show config list changes", ]
        if user:
            # FIXME: sanitize username?
            cmd.append("partial admin {}".format(user))
        cmd = ' '.join(cmd)
        self.xapi.op(cmd=cmd, cmd_xml=True)
        changes = self._get_result()
        return changes['response']['result']['journal']['entry']

    def get_config_log(self, user=None, nlogs=100):
        log_filter = []
        if user:
            # FIXME: sanitize username?
            log_filter.append("( admin eq %s )" % user)

        if not log_filter:
            log_filter = None

        self.xapi.log(log_type='config', nlogs=nlogs,
                      log_filter=log_filter)
        logs = self._get_result()
        return logs['response']['result']['log']['logs']['entry']
