from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate
)
from friendships.models import HBaseFollower, HBaseFollowing, Friendship
from friendships.services import FriendshipService
from gatekeeper.models import GateKeeper
from ratelimit.decorators import ratelimit
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from utils.paginations import EndlessPagination


class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate
    pagination_class = EndlessPagination

    @action(methods=['get'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followers(self, request, pk):
        """
        Get a list of followers based on to_user_id
        pk should be to_user_id
        GET /api/friendships/<pk>/followers/
        """
        pk = int(pk) # In case type transform in paginator
        paginator = self.paginator
        if GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            page = paginator.paginate_hbase(HBaseFollower, (pk,), request)
        else:
            friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
            page = paginator.paginate_queryset(friendships, request)
        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    @action(methods=['get'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followings(self, request, pk):
        """
        Get a list of followings user based on from_user_id
        pk should be from_user_id
        GET /api/friendships/<pk>/followings/
        """
        pk = int(pk)
        paginator = self.paginator
        if GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            page = paginator.paginate_hbase(HBaseFollowing, (pk,), request)
        else:
            friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
            page = paginator.paginate_queryset(friendships, request)
        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def follow(self, request, pk):
        """
        Create follow relationship between logged-in user (from_user_id) and some to_user_id
        pk should be to_user_id
        POST /api/friendships/<pk>/follow
        """
        to_follow_user = self.get_object()
        # get_object can help us to check whether the pk is exist
        # get_object will load the queryset in this viewset
        # Then its get_object_or_404 will examine whether the user exists
        if FriendshipService.has_followed(request.user.id, to_follow_user.id):
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)

        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': to_follow_user.id,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        instance = serializer.save()
        # FriendshipService.invalidate_following_cache(request.user.id)
        # # Manually invalidate the following cache for any changes
        # # Disadvantage: 
        # # 1. if we forget to add this line of code for some functions, cache will not be invalided
        # # 2. Also, this cannot be applied via admin panel
        # # To solve the both problem, we can add signal to the Friendship model -> go and checkout
        return Response(
            FollowingSerializer(instance, context={'request': request}).data, 
            status=status.HTTP_201_CREATED,
        )

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def unfollow(self, request, pk):
        unfollow_user = self.get_object()
        if request.user.id == unfollow_user.id:
            return Response({
                'success': False,
                'error': 'you cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        deleted = FriendshipService.unfollow(request.user.id, unfollow_user.id)
        return Response({
            'success': True,
            'deleted': deleted,
        }, status=status.HTTP_200_OK)

    def list(self,request):
        """
        list function is for the GET function at the root endpoint of this API viewset
        Here I would like to provided a more restful API endpoint for followings/follower
        """
        if request.query_params['type'] == 'followers':
            if 'to_user_id' not in request.query_params:
                return Response({
                    'message': 'mandatory parameter must exist (to_user_id for this type)',
                    'error': 'lack of mandatory parameter',
                }, status=400)
                # verify mandatory parameter must exist
            friendships = Friendship.objects.filter(to_user_id=request.query_params['to_user_id']).order_by('-created_at')
            serializer = FollowerSerializer(friendships, many=True)
            return Response({'followers': serializer.data}, status=status.HTTP_200_OK)
            # return followers of an account
        
        elif request.query_params['type'] == 'followings':
            if 'from_user_id' not in request.query_params:
                return Response({
                    'message': 'mandatory parameter must exist (from_user_id for this type)',
                    'error': 'lack of mandatory parameter',
                }, status=400)
                # verify mandatory parameter must exist
            friendships = Friendship.objects.filter(from_user_id=request.query_params['from_user_id']).order_by('-created_at')

            if 'to_user_id' in request.query_params:
                is_following = friendships.filter(to_user_id=request.query_params['to_user_id']).exists()
                return Response({'is_following': is_following}, status=status.HTTP_200_OK)
                # check the following relationship between from_user_id and to_user_id
            
            serializer = FollowingSerializer(friendships, many=True)
            return Response({'followings': serializer.data}, status=status.HTTP_200_OK)
            # return the followings list of an account

        return Response(Response({
            'message': 'This is friendship API, please define request type in get parm (followers/followings)'
        }))
        # default return with no useful information
