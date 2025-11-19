from datetime import datetime
from typing import Any, Dict, Optional


def save_weather(doc: Dict[str, Any]) -> Optional[Any]:
	"""Save weather document using repository.mongo.insert_document.

	Adds a UTC `fetched_at` if missing. Returns inserted_id on success or None on failure.
	"""
	try:
		# add a fetched_at timestamp if not provided
		if "fetched_at" not in doc:
			doc["fetched_at"] = datetime.utcnow()

		# import lazily to avoid import cycles when module imported elsewhere
		from .repository import mongo as repo_mongo

		return repo_mongo.insert_document(doc)
	except Exception as exc:
		# don't let storage errors crash RPC handling; log and return None
		print("storage.save_weather error:", exc)
		return None

