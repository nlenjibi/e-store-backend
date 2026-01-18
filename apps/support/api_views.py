"""
Support API Views
-----------------
Additional API endpoints for support features.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class HelpSupportSettingsView(APIView):
    """Get help and support settings."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'success': True,
            'settings': {
                'email': 'support@modernecommerce.com',
                'phone': '+1-800-123-4567',
                'hours': 'Monday - Friday: 9:00 AM - 6:00 PM EST',
                'faqUrl': '/help/faq',
                'contactUrl': '/help/contact'
            }
        })


class SocialLinksView(APIView):
    """Get social media links."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'success': True,
            'links': [
                {
                    'id': 1,
                    'platform': 'facebook',
                    'url': 'https://facebook.com/modernecommerce',
                    'icon': 'facebook'
                },
                {
                    'id': 2,
                    'platform': 'twitter',
                    'url': 'https://twitter.com/modernecommerce',
                    'icon': 'twitter'
                },
                {
                    'id': 3,
                    'platform': 'instagram',
                    'url': 'https://instagram.com/modernecommerce',
                    'icon': 'instagram'
                },
                {
                    'id': 4,
                    'platform': 'linkedin',
                    'url': 'https://linkedin.com/company/modernecommerce',
                    'icon': 'linkedin'
                }
            ]
        })


class AppDownloadLinksView(APIView):
    """Get mobile app download links."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'success': True,
            'links': {
                'ios': {
                    'url': 'https://apps.apple.com/app/modernecommerce',
                    'available': True
                },
                'android': {
                    'url': 'https://play.google.com/store/apps/details?id=com.modernecommerce',
                    'available': True
                }
            }
        })
