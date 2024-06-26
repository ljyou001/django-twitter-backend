from django.contrib.auth.models import User
from rest_framework import exceptions, serializers

from accounts.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserSerializerWithProfile(serializers.ModelSerializer):
    nickname = serializers.CharField(source='profile.nickname')
    # this means when you passed a user instance to the serializer
    # it will access user.profile.nickname
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None
    
    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'avatar_url')


class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('nickname', 'avatar')


class UserSerializerForTweets(UserSerializerWithProfile):
    pass


class UserSerializerForFriendship(UserSerializerWithProfile):
    pass


class UserSerializerForComment(UserSerializerWithProfile):
    pass


class UserSerializerForLikes(UserSerializerWithProfile):
    pass


class LoginSerializer(serializers.Serializer):
    # 仅用来帮助检测是否有这两项，CharField里面required默认为True
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        if not User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({'username': 'Username does not exist'})
        return data

      
class SignupSerializer(serializers.ModelSerializer):
    # why ModelSerializer: We hope the user will be created in the end
    username = serializers.CharField(max_length=30, min_length=3)
    password = serializers.CharField(max_length=30, min_length=3)
    email = serializers.EmailField()
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    # will be called when is_valid() called
    def validate(self, data):
        if User.objects.filter(username=data['username'].lower()).exists():
            # always .lower(), You can also user
            # User.objects.filter(username__iexact=data['username']), where i means ignore cases, very low effeciency 
            raise serializers.ValidationError({'username': 'Username already exists'})
        if User.objects.filter(email=data['email'].lower()).exists():
            raise serializers.ValidationError({'username': 'Email already exists'})
        return data
    
    # will be called when save() called
    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        # Why the following format is wrong?
        # user = User.objects.create_user(
        #     username=username,
        #     ...
        # )
        # Go check the source code of create_user
        # In _create_user, you can see the password processing. set_password(password)
        
        user.profile
        # Create user profile
        
        return user
