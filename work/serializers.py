from work.models import Property, Job, Shift, Client
from rest_framework import serializers

class ShiftSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shift
        fields = ('date',)

class JobSerializer(serializers.ModelSerializer):
    job_shift = ShiftSerializer()
    
    class Meta:
        model = Job
        fields = ('job_shift',)

class PropertySerializer(serializers.HyperlinkedModelSerializer):
    location = JobSerializer(many=True)

    class Meta:
        model = Property
        fields = ('name','location')
