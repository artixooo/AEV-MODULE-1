from urllib.parse import urlencode

from app.schemas.oauth import (
    OAuthAuthorizationRequest,
    OAuthCallbackRequest,
    OAuthProviderConfig,
)


class OAuthService:
    """OAuth 2.0 authorization flow interface."""

    @staticmethod
    def build_authorization_url(
        config: OAuthProviderConfig,
        request: OAuthAuthorizationRequest,
    ) -> str:
        """Build the provider authorization URL."""

        params = {
            "client_id": config.client_id,
            "redirect_uri": str(request.redirect_uri),
            "response_type": "code",
            "scope": " ".join(request.scopes or config.scopes),
            "state": request.state,
        }

        return f"{config.authorization_url}?{urlencode(params)}"

    @staticmethod
    def validate_callback(
        callback: OAuthCallbackRequest,
    ) -> None:
        """Validate the basic OAuth callback contract."""

        if callback.error:
            raise ValueError(
                callback.error_description or callback.error
            )

        if not callback.code:
            raise ValueError("OAuth authorization code is required")

        if not callback.state:
            raise ValueError("OAuth state is required")
