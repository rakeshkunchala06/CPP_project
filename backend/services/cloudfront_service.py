"""
Amazon CloudFront Service Wrapper.

Manages CDN distribution for frontend static assets.
Returns mock URLs in local mode.
"""


class CloudFrontService:
    """Wrapper for Amazon CloudFront operations."""

    def __init__(self, use_mock=True, domain=None):
        self.use_mock = use_mock
        self.domain = domain or "d1234567890.cloudfront.net"
        self._mock_invalidations = []

    def get_distribution_url(self, path=""):
        """Get the full CloudFront URL for an asset."""
        if self.use_mock:
            return f"https://{self.domain}/{path}" if path else f"https://{self.domain}"
        return f"https://{self.domain}/{path}"

    def create_invalidation(self, paths):
        """Invalidate cached assets at the given paths."""
        if self.use_mock:
            invalidation_id = f"INV-{len(self._mock_invalidations) + 1}"
            self._mock_invalidations.append({
                "invalidation_id": invalidation_id,
                "paths": paths,
                "status": "completed",
            })
            return {
                "invalidation_id": invalidation_id,
                "status": "completed",
                "mode": "mock",
            }
        return {"status": "created"}

    def get_distribution_info(self):
        """Get information about the CloudFront distribution."""
        return {
            "domain": self.domain,
            "status": "deployed",
            "price_class": "PriceClass_100",
            "origins": ["transit-planner-assets.s3.amazonaws.com"],
            "mode": "mock" if self.use_mock else "production",
        }

    def health_check(self):
        return {
            "service": "Amazon CloudFront",
            "status": "healthy",
            "mode": "local_mock" if self.use_mock else "production",
            "domain": self.domain,
            "invalidations_count": len(self._mock_invalidations),
        }
