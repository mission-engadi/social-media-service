"""Provider factory for dependency injection.

This module provides a factory pattern for creating social media provider instances
based on configuration settings.
"""

import logging
from typing import Optional

from app.core.config import settings
from app.services.providers.base_provider import SocialMediaProvider, ProviderError
from app.services.providers.ayrshare_provider import AyrshareProvider
from app.services.providers.buffer_provider import BufferProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory for creating social media provider instances.
    
    This factory creates provider instances based on the configured provider type.
    Supports Ayrshare (default) and Buffer providers.
    """
    
    # Registry of available providers
    _providers = {
        'ayrshare': AyrshareProvider,
        'buffer': BufferProvider,
    }
    
    @classmethod
    def create(
        cls,
        provider_type: Optional[str] = None,
        **kwargs
    ) -> SocialMediaProvider:
        """Create a provider instance.
        
        Args:
            provider_type: Type of provider ('ayrshare' or 'buffer').
                          If None, uses SOCIAL_MEDIA_PROVIDER from settings.
            **kwargs: Additional arguments to pass to provider constructor
                     (e.g., api_key, access_token)
        
        Returns:
            Provider instance implementing SocialMediaProvider interface
        
        Raises:
            ProviderError: If provider type is not supported
        
        Example:
            >>> provider = ProviderFactory.create('ayrshare', api_key='your-key')
            >>> provider = ProviderFactory.create()  # Uses default from settings
        """
        # Get provider type from settings if not specified
        if provider_type is None:
            provider_type = getattr(settings, 'SOCIAL_MEDIA_PROVIDER', 'ayrshare')
        
        # Normalize provider type
        provider_type = provider_type.lower().strip()
        
        # Get provider class
        provider_class = cls._providers.get(provider_type)
        
        if provider_class is None:
            available = ', '.join(cls._providers.keys())
            raise ProviderError(
                f"Unsupported provider type: '{provider_type}'. "
                f"Available providers: {available}"
            )
        
        # Create and return provider instance
        try:
            provider = provider_class(**kwargs)
            logger.info(f"Created {provider_type} provider instance")
            return provider
        except Exception as e:
            logger.error(f"Failed to create {provider_type} provider: {e}")
            raise ProviderError(f"Failed to create provider: {str(e)}")
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """Register a custom provider.
        
        This method allows you to extend the factory with custom provider implementations.
        
        Args:
            name: Provider name (e.g., 'custom_provider')
            provider_class: Provider class that implements SocialMediaProvider
        
        Raises:
            ValueError: If provider_class doesn't implement SocialMediaProvider
        
        Example:
            >>> class CustomProvider(SocialMediaProvider):
            ...     # Implementation
            >>> ProviderFactory.register_provider('custom', CustomProvider)
        """
        if not issubclass(provider_class, SocialMediaProvider):
            raise ValueError(
                f"Provider class must implement SocialMediaProvider interface. "
                f"Got: {provider_class}"
            )
        
        cls._providers[name.lower().strip()] = provider_class
        logger.info(f"Registered custom provider: {name}")
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names.
        
        Returns:
            List of registered provider names
        """
        return list(cls._providers.keys())


# Convenience function for getting provider instance
def get_provider(
    provider_type: Optional[str] = None,
    **kwargs
) -> SocialMediaProvider:
    """Convenience function to get a provider instance.
    
    This is a shorthand for ProviderFactory.create() and is useful
    for dependency injection in FastAPI routes.
    
    Args:
        provider_type: Type of provider ('ayrshare' or 'buffer').
                      If None, uses SOCIAL_MEDIA_PROVIDER from settings.
        **kwargs: Additional arguments to pass to provider constructor
    
    Returns:
        Provider instance implementing SocialMediaProvider interface
    
    Example:
        >>> # In FastAPI dependency
        >>> async def get_current_provider() -> SocialMediaProvider:
        ...     return get_provider()
        >>>
        >>> @app.get("/posts")
        >>> async def list_posts(provider: SocialMediaProvider = Depends(get_current_provider)):
        ...     profiles = await provider.get_profiles()
        ...     return profiles
    """
    return ProviderFactory.create(provider_type, **kwargs)
