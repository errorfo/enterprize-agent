from typing import Callable, Dict, Any
import uuid
import time

class A2AMessage:
	def __init__(self, sender: str, receiver: str, type: str, payload: Dict[str, Any]):
		self.id = str(uuid.uuid4())
		self.sender = sender
		self.receiver = receiver
		self.type = type
		self.payload = payload
		self.timestamp = time.time()

	def to_dict(self):
		return {
			'id': self.id,
			'sender': self.sender,
			'receiver': self.receiver,
			'type': self.type,
			'payload': self.payload,
			'timestamp': self.timestamp,
		}

# Simple in-process dispatcher
class Dispatcher:
	def __init__(self):
		self._handlers = {}

	def register(self, agent_name: str, handler: Callable[[A2AMessage], None]):
		self._handlers[agent_name] = handler

	def send(self, msg: A2AMessage):
		handler = self._handlers.get(msg.receiver)
		if handler:
			handler(msg)
		else:
			raise ValueError(f"No handler registered for {msg.receiver}")

# Example handlers (used in integration tests/demo)
if __name__ == '__main__':
	disp = Dispatcher()

	def ingestion_handler(msg: A2AMessage):
		print('Ingestion agent received message:', msg.to_dict())

	def vision_handler(msg: A2AMessage):
		print('Vision agent received message:', msg.to_dict())

	disp.register('ingestion', ingestion_handler)
	disp.register('vision', vision_handler)
	m = A2AMessage(sender='test', receiver='vision', type='process_image',
				   payload={'image_id': 1})
	disp.send(m)