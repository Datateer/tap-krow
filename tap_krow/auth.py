"""krow Authentication."""


from singer_sdk.authenticators import SimpleAuthenticator


class krowAuthenticator(SimpleAuthenticator):
    """Authenticator class for krow."""

    @classmethod
    def create_for_stream(cls, stream) -> "krowAuthenticator":
        return cls(
            stream=stream,
            auth_headers={"Authorization": f'Bearer {stream.config.get("api_key")}'},
        )
