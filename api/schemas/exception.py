from typing import TypedDict


class AppException(TypedDict):
	path: str
	method: str
	error_type: str
	error: str
