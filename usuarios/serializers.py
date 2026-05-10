from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Usuario, Rol, Recurso, UsuarioRol, RolRecurso


# ==============================================================================
# Auth
# ==============================================================================

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Credenciales inválidas.')
        if not user.is_active or not user.estado:
            raise serializers.ValidationError('Usuario inactivo.')
        data['user'] = user
        return data

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


# ==============================================================================
# Recursos
# ==============================================================================

class RecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recurso
        fields = '__all__'


class RecursoTreeSerializer(serializers.ModelSerializer):
    """Serializer que incluye hijos para construir el árbol de menú."""
    hijos = serializers.SerializerMethodField()

    class Meta:
        model = Recurso
        fields = '__all__'

    def get_hijos(self, obj):
        return RecursoTreeSerializer(
            obj.hijos.filter(estado=True).order_by('orden'), many=True
        ).data


# ==============================================================================
# Roles
# ==============================================================================

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


# ==============================================================================
# Usuarios
# ==============================================================================

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    roles = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Usuario
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'telefono', 'estado', 'is_staff', 'password', 'roles',
        )

    def get_roles(self, obj):
        return obj.roles_list

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Usuario(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# ==============================================================================
# UsuarioRol / RolRecurso
# ==============================================================================

class UsuarioRolSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

    class Meta:
        model = UsuarioRol
        fields = ('id', 'usuario', 'rol', 'usuario_username', 'rol_nombre')


class RolRecursoSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    recurso_nombre = serializers.CharField(source='recurso.nombre', read_only=True)

    class Meta:
        model = RolRecurso
        fields = ('id', 'rol', 'recurso', 'rol_nombre', 'recurso_nombre')
