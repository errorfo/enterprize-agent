import argparse
import requests
from flask import Flask, request, jsonify, send_from_directory
import threading
import os

MOCK_HOST = 'http://127.0.0.1:9000'
app = Flask('mock_ticketing')
_tickets = []
_next = 1

@app.route('/create_ticket', methods=['POST'])
def create_ticket_endpoint():
    global _next
    body = request.json or {}
    ticket = {
        'id': _next,
        'title': body.get('title'),
        'description': body.get('description'),
        'priority': body.get('priority', 'medium')
    }
    _tickets.append(ticket)
    _next += 1
    return jsonify(ticket), 201

@app.route('/tickets', methods=['GET'])
def list_tickets_endpoint():
    return jsonify(_tickets)

@app.route('/openapi.yaml', methods=['GET'])
def serve_openapi_yaml():
    directory = os.path.dirname(__file__)
    if os.path.exists(os.path.join(directory, 'openapi_ticketing.yaml')):
        return send_from_directory(directory, 'openapi_ticketing.yaml')
    return jsonify({'error': 'spec not found'}), 404

@app.route('/openapi.json', methods=['GET'])
def serve_openapi_json():
    # Optional: convert YAML to JSON on the fly (requires pyyaml) or serve a preconverted file
    directory = os.path.dirname(__file__)
    json_path = os.path.join(directory, 'openapi_ticketing.json')
    if os.path.exists(json_path):
        return send_from_directory(directory, 'openapi_ticketing.json')
    return jsonify({'error': 'json spec not found'}), 404

class MockTicketingClient:
    def __init__(self, base_url=MOCK_HOST, timeout=5):
        self.base_url = base_url
        self.timeout = timeout
    
    def create_ticket(self, title: str, description: str, priority: str = 'medium'):
        payload = {'title': title, 'description': description, 'priority': priority}
        resp = requests.post(f"{self.base_url}/create_ticket", json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

def serve_mock():
    app.run(port=9000)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--serve', action='store_true')
    args = parser.parse_args()
    if args.serve:
        print('Starting mock ticketing server on http://127.0.0.1:9000')
        serve_mock()