import requests
import yaml

OPENAPI_URL = 'http://127.0.0.1:9000/openapi.yaml'

# --- Fallback raw client (works anywhere) ---
class TicketToolRaw:
    def __init__(self, base_url='http://127.0.0.1:9000'):
        self.base_url = base_url
    
    def create_ticket(self, title, description, priority='medium'):
        resp = requests.post(f"{self.base_url}/create_ticket", json={'title':
            title, 'description': description, 'priority': priority}, timeout=5)
        resp.raise_for_status()
        return resp.json()

# --- Try to load spec (optional) ---
def load_openapi_spec(url=OPENAPI_URL):
    r = requests.get(url)
    r.raise_for_status()
    return yaml.safe_load(r.text)

# --- ADK-style wrapper pattern ---
class OpenAPIToolWrapper:
    def __init__(self, spec_url=OPENAPI_URL):
        self.spec = load_openapi_spec(spec_url)
        # You could dynamically generate method signatures here based on spec paths
    
    def create_ticket(self, title, description, priority='medium'):
        # Simple direct call; in a full ADK integration the tool loader would do this
        raw = TicketToolRaw()
        return raw.create_ticket(title, description, priority)

# Example usage
if __name__ == '__main__':
    wrapper = OpenAPIToolWrapper()
    print('Spec loaded keys:', list(wrapper.spec.keys()))
    res = wrapper.create_ticket('Test from ADK wrapper', 'This is a test',
        'high')
    print('Created ticket:', res)