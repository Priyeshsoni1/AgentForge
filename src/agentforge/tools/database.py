USERS = {
    "101": {"name": "Rahul", "role": "Engineer"},
    "102": {"name": "Priya", "role": "Manager"},
}


def database_lookup(user_id: str) -> str:
    user = USERS.get(user_id)

    if not user:
        return f"User {user_id} not found"

    return str(user)