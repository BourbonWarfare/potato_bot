class ForumId(int):
    def __new__(cls, value: int | str) -> "ForumId":
        return super().__new__(cls, int(value))

    def __repr__(self) -> str:
        return f"ForumId({super().__repr__()})"
