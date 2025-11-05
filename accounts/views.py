from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import CustomUser
from .serializers import UserSerializer, UserLoginSerializer, UserCreateSerializer, RegisterSerializer
from .permissions import *

# ============ AUTHENTICATION VIEWS ============

@swagger_auto_schema(
    method='post',
    operation_description="Foydalanuvchi tizimga kirishi",
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response(
            description="Muvaffaqiyatli login",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: openapi.Response(description="Noto'g'ri ma'lumotlar"),
        403: openapi.Response(description="Hisob faol emas")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Faol bo'lmagan foydalanuvchilarni tekshirish
            if not user.is_active:
                return Response({
                    'error': 'Hisobingiz hali faollashtirilmagan. Iltimos, admin bilan bog\'laning.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # JWT token yaratish
            refresh = RefreshToken.for_user(user)
            
            user_data = UserSerializer(user).data
            
            return Response({
                'message': 'Login successful',
                'user': user_data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response(
            {'error': f'Server xatosi: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    operation_description="Ro'yxatdan o'tish so'rovi yuborish",
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response(
            description="Ro'yxatdan o'tish so'rovi muvaffaqiyatli yuborildi",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'note': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: openapi.Response(description="Noto'g'ri ma'lumotlar")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    try:
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'message': 'Ro\'yxatdan o\'tish so\'rovi muvaffaqiyatli yuborildi',
                'user_id': user.id,
                'note': 'Admin tomonidan tasdiqlangandan so\'ng hisobingiz faollashtiriladi.'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response(
            {'error': f'Server xatosi: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    operation_description="Token yangilash",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['refresh'],
        properties={
            'refresh': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Refresh token'
            )
        }
    ),
    responses={
        200: openapi.Response(
            description="Token yangilandi",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: openapi.Response(description="Noto'g'ri token")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """Token yangilash uchun endpoint"""
    try:
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'refresh token maydoni kiritilishi shart'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        
        return Response({
            'access': str(token.access_token)
        }, status=status.HTTP_200_OK)
        
    except TokenError as e:
        return Response(
            {'error': f'Yaroqsiz token: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Server xatosi: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@swagger_auto_schema(
    method='post',
    operation_description="Tizimdan chiqish",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['refresh'],
        properties={
            'refresh': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Refresh token'
            )
        }
    ),
    responses={
        200: openapi.Response(
            description="Muvaffaqiyatli chiqish",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: openapi.Response(description="Noto'g'ri token"),
        401: openapi.Response(description="Avtorizatsiyadan o'tilmagan")
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'refresh token maydoni kiritilishi shart'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Token ni tekshirish va blacklist ga qo'shish
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response(
            {'message': 'Muvaffaqiyatli chiqildi'}, 
            status=status.HTTP_200_OK
        )
        
    except TokenError as e:
        return Response(
            {'error': f'Yaroqsiz token: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Server xatosi: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


# ============ PROFILE & AUTH CHECK VIEWS ============

@swagger_auto_schema(
    method='get',
    operation_description="Joriy foydalanuvchi profilini olish",
    responses={
        200: UserSerializer,
        401: openapi.Response(description="Avtorizatsiyadan o'tilmagan")
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    try:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': f'Server xatosi: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='get',
    operation_description="Avtorizatsiyani tekshirish",
    responses={
        200: openapi.Response(
            description="Avtorizatsiya muvaffaqiyatli",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(type=openapi.TYPE_STRING),
                    'is_authenticated': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'role': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        401: openapi.Response(description="Avtorizatsiyadan o'tilmagan")
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth(request):
    """Avtorizatsiyani tekshirish uchun endpoint"""
    return Response({
        'user': request.user.username,
        'is_authenticated': request.user.is_authenticated,
        'role': request.user.role
    })


# ============ USER MANAGEMENT VIEWS ============

@swagger_auto_schema(
    method='post',
    operation_description="Yangi foydalanuvchi yaratish (faqat Super Admin)",
    request_body=UserCreateSerializer,
    responses={
        201: openapi.Response(description="Foydalanuvchi yaratildi", schema=UserSerializer),
        400: openapi.Response(description="Noto'g'ri ma'lumotlar"),
        403: openapi.Response(description="Ruxsat etilmagan")
    }
)
@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def create_user(request):
    try:
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User created successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response(
            {'error': f'Server xatosi: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    operation_description="Foydalanuvchini faollashtirish (Admin)",
    responses={
        200: openapi.Response(
            description="Foydalanuvchi muvaffaqiyatli faollashtirildi",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            )
        ),
        404: openapi.Response(description="Foydalanuvchi topilmadi"),
        403: openapi.Response(description="Ruxsat etilmagan")
    }
)
@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def activate_user(request, user_id):
    """Admin tomonidan foydalanuvchini faollashtirish"""
    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_active = True
        user.save()
        
        return Response({
            'message': 'Foydalanuvchi muvaffaqiyatli faollashtirildi',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'Foydalanuvchi topilmadi'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@swagger_auto_schema(
    method='post',
    operation_description="Foydalanuvchini faolsizlantirish (Admin)",
    responses={
        200: openapi.Response(
            description="Foydalanuvchi muvaffaqiyatli faolsizlantirildi",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            )
        ),
        404: openapi.Response(description="Foydalanuvchi topilmadi"),
        403: openapi.Response(description="Ruxsat etilmagan")
    }
)
@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def deactivate_user(request, user_id):
    """Admin tomonidan foydalanuvchini faolsizlantirish"""
    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_active = False
        user.save()
        
        return Response({
            'message': 'Foydalanuvchi muvaffaqiyatli faolsizlantirildi',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'Foydalanuvchi topilmadi'}, 
            status=status.HTTP_404_NOT_FOUND
        )


# ============ USER LIST VIEWS ============

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [CanManageUsers]
    
    @swagger_auto_schema(
        operation_description="Foydalanuvchilar ro'yxatini olish",
        responses={
            200: UserSerializer(many=True),
            403: openapi.Response(description="Ruxsat etilmagan")
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return CustomUser.objects.all()
        elif user.role == 'main_warehouse_admin':
            return CustomUser.objects.filter(
                role__in=['warehouse_admin', 'main_warehouse_forwarder', 'warehouse_receiver']
            )
        return CustomUser.objects.none()


class PendingUsersListView(generics.ListAPIView):
    """Faollashtirish kutilayotgan foydalanuvchilar ro'yxati"""
    serializer_class = UserSerializer
    permission_classes = [CanManageUsers]
    
    @swagger_auto_schema(
        operation_description="Faollashtirish kutilayotgan foydalanuvchilar ro'yxati",
        responses={
            200: UserSerializer(many=True),
            403: openapi.Response(description="Ruxsat etilmagan")
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        return CustomUser.objects.filter(is_active=False)