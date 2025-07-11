from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'DELETE':
            return False
        # Instance must have an attribute named `owner`.
        if request.user.is_authenticated:
            if request.user.is_admin:
                return True
            return obj.user.username == request.user.username
        else:
            return False


class IsOwnerOfCar(permissions.BasePermission):
    """
    Custom permission to only allow owners of a car to edit or delete its images.
    """

    def has_object_permission(self, request, view, obj):
        return obj.ad.user.username == request.user.username


class HasViewAuction(permissions.BasePermission):
    """
    Custom permission to see auctions .
    """

    def has_permission(self, request, view):
        return bool(request.user.profile.view_auction)
