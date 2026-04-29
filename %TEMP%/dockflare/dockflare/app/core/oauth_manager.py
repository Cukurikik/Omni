# DockFlare: Automates Cloudflare Tunnel ingress from Docker labels.
# Copyright (C) 2025 ChrispyBacon-Dev <https://github.com/ChrispyBacon-dev/DockFlare>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# dockflare/app/core/oauth_manager.py

import logging


def register_oauth_providers(flask_app, oauth_instance, fernet):
    """
    Register OAuth providers with the OAuth instance.

    This function can be called both at startup and when configuration changes
    to enable hot-reloading of OAuth providers without restart.

    Args:
        flask_app: Flask application instance
        oauth_instance: Authlib OAuth instance
        fernet: Fernet cipher instance for decrypting credentials
    """
        
    if hasattr(oauth_instance, '_clients'):
        oauth_instance._clients.clear()
        logging.info("Cleared existing OAuth provider registrations")

    providers = flask_app.config.get('OAUTH_PROVIDERS', [])
    registered_count = 0

    for provider in providers:
        if not provider.get('enabled', True):
            logging.info(f"Skipping disabled OAuth provider: {provider.get('name')}")
            continue

        try:
            client_id = fernet.decrypt(provider['client_id'].encode()).decode()
            client_secret = fernet.decrypt(provider['client_secret'].encode()).decode()
        except Exception as e:
            logging.error(f"Could not decrypt credentials for provider {provider.get('name')}. Skipping. Error: {e}")
            continue

        provider_type = provider.get('type')
        provider_id = provider.get('id')
        issuer_url = provider.get('issuer_url')

        # GitHub provider (uses OAuth 2.0, not OIDC)
        if provider_type == 'github':
            oauth_instance.register(
                name=provider_id,
                client_id=client_id,
                client_secret=client_secret,
                authorize_url='https://github.com/login/oauth/authorize',
                access_token_url='https://github.com/login/oauth/access_token',
                api_base_url='https://api.github.com/',
                client_kwargs={'scope': 'user:email'}
            )
            logging.info(f"Registered GitHub OAuth provider: {provider.get('name')} (id: {provider_id})")
            registered_count += 1
            continue

        # OIDC providers (Google, Authentik, etc.)
        if not issuer_url:
            if provider_type == 'google':
                issuer_url = 'https://accounts.google.com'
            else:
                logging.warning(f"Provider '{provider.get('name')}' is of type '{provider_type}' but is missing an issuer_url. It will be skipped.")
                continue

        if not issuer_url.endswith('/'):
            issuer_url += '/'

        metadata_url = f"{issuer_url}.well-known/openid-configuration"

        try:
            oauth_instance.register(
                name=provider_id,
                client_id=client_id,
                client_secret=client_secret,
                server_metadata_url=metadata_url,
                client_kwargs={'scope': 'openid email profile'}
            )
            logging.info(f"Registered OIDC provider: {provider.get('name')} (id: {provider_id}, type: {provider_type})")
            registered_count += 1
        except Exception as e:
            logging.error(f"Failed to register OIDC provider {provider.get('name')}: {e}", exc_info=True)

    logging.info(f"OAuth provider registration complete: {registered_count} provider(s) registered")
    return registered_count
