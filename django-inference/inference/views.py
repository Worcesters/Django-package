from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class InferenceHealthView(APIView):
    '''Endpoint sante minimal pour inference.

    MRO:
    1. APIView.get -> reponse JSON
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        return Response({"app": "inference", "status": "ok"})