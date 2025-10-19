from axb.models import AxConfig
from axb.axclient import _AxClient

def create_client_from_json(ax_json):
    return _AxClient().from_json_snapshot(ax_json)
