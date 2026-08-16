USERS = {
    "101": {"name": "Rahul", "role": "Engineer"},
    "102": {"name": "Priya", "role": "Manager"},
}


def database_lookup(user_id: str) -> str:
    if not user_id:
        raise ValueError("user_id is required")

    user = USERS.get(user_id)

    if not user:
        raise ValueError(f"User {user_id} not found")

    return str(user)