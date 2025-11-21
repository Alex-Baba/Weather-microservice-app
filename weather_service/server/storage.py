from datetime import datetime
from typing import Any, Dict, Optional

"""Thin storage wrapper delegating to `repository.mongo`.

This module is a small compatibility layer so other modules can call
`storage.save_weather(...)` while the repository contains the DB logic.
"""


def save_weather(doc: Dict[str, Any]) -> Optional[Any]:
	# ensure a fetched_at timestamp exists
	# Save time in the local timezone (timezone-aware) so DB stores the user's local time
	if "fetched_at" not in doc:
		# datetime.now().astimezone() yields a timezone-aware local datetime
		doc["fetched_at"] = datetime.now().astimezone()

	try:
		from .repository import mongo as repo_mongo

		return repo_mongo.insert_document(doc)
	except Exception as exc:
		# Avoid crashing callers; log and return None
		print("storage.save_weather error:", exc)
		return None


