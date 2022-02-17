from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import View

class MotorStep1(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_31.djhtml')

class MotorStep2(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_32.djhtml')

class MotorStep3(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_35.djhtml')

class MotorStep4(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_33.djhtml')

class MotorStep5(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_34.djhtml')

class MotorStep6(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_63.djhtml')

class MotorStep7(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_36.djhtml')

class MotorStep8(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_37.djhtml')

class MotorStep9(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_38.djhtml')

class MotorStep10(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_39.djhtml')

class MotorStep11(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_41.djhtml')

class MotorStep12(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_40.djhtml')

class MotorStep13(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_42.djhtml')

class MotorStep14(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_44.djhtml')

class MotorStep15(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_46.djhtml')

class MotorStep16(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_71.djhtml')

class MotorStep17(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_72.djhtml')

class MotorStep18(LoginRequiredMixin, View):
    def get(self, request):
        return render(request,'motorinsurance/deal/landing_47.djhtml')