from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .models import Usuario, Rol, Recurso, UsuarioRol, RolRecurso
from .serializers import (
    LoginSerializer,
    UsuarioSerializer,
    RolSerializer,
    RecursoSerializer,
    UsuarioRolSerializer,
    RolRecursoSerializer,
)
from .permissions import IsAdminOrStaff


# ==============================================================================
# Auth
# ==============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data['user']
    tokens = serializer.get_tokens(user)

    recursos = user.recursos_list
    return Response({
        **tokens,
        'usuario': UsuarioSerializer(user).data,
        'roles': RolSerializer(
            Rol.objects.filter(usuario_roles__usuario=user, estado=True), many=True
        ).data,
        'recursos': RecursoSerializer(recursos, many=True).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        pass
    return Response({'detail': 'Sesión cerrada.'}, status=status.HTTP_205_RESET_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UsuarioSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# ==============================================================================
# Usuarios
# ==============================================================================

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by('username')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filterset_fields = ['estado', 'is_staff']


# ==============================================================================
# Roles
# ==============================================================================

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all().order_by('nombre')
    serializer_class = RolSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion']


# ==============================================================================
# Recursos
# ==============================================================================

class RecursoViewSet(viewsets.ModelViewSet):
    queryset = Recurso.objects.all().order_by('orden', 'nombre')
    serializer_class = RecursoSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['estado', 'recurso_padre']
    search_fields = ['nombre', 'path', 'url_frontend']


# ==============================================================================
# UsuarioRol
# ==============================================================================

class UsuarioRolViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRol.objects.select_related('usuario', 'rol').all()
    serializer_class = UsuarioRolSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['usuario', 'rol']


# ==============================================================================
# RolRecurso
# ==============================================================================

class RolRecursoViewSet(viewsets.ModelViewSet):
    queryset = RolRecurso.objects.select_related('rol', 'recurso').all()
    serializer_class = RolRecursoSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['rol', 'recurso']
