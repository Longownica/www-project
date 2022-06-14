from api.models import CheckersGame
from rest_framework import serializers
class CheckersGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckersGame
        fields = '__all__'