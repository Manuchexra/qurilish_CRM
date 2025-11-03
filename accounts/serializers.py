from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'phone_number', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        help_text="Foydalanuvchi nomi"
    )
    password = serializers.CharField(
        help_text="Parol",
        style={'input_type': 'password'}
    )

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('Foydalanuvchi hisobi bloklangan.')
            else:
                raise serializers.ValidationError('Noto\'g\'ri login yoki parol.')
        else:
            raise serializers.ValidationError('Login va parol kiritilishi shart.')
        
        return data

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        help_text="Parol (kamida 8 ta belgi)",
        style={'input_type': 'password'},
        min_length=8
    )
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'phone_number', 'password')
        extra_kwargs = {
            'username': {'help_text': 'Foydalanuvchi nomi (unique)'},
            'email': {'help_text': 'Elektron pochta manzili'},
            'first_name': {'help_text': 'Ism'},
            'last_name': {'help_text': 'Familiya'},
            'role': {'help_text': 'Foydalanuvchi roli'},
            'phone_number': {'help_text': 'Telefon raqami'},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu foydalanuvchi nomi allaqachon mavjud.")
        return value

    def validate_email(self, value):
        if value and CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email allaqachon mavjud.")
        return value