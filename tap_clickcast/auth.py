"""clickcast Authentication."""


from singer_sdk.authenticators import SimpleAuthenticator


class clickcastAuthenticator(SimpleAuthenticator):
    """Authenticator class for clickcast."""

    @classmethod
    def create_for_stream(cls, stream) -> "clickcastAuthenticator":
        return cls(
            stream=stream,
            auth_headers={"X-Partner-Token": stream.config.get("partner_token")},
        )
