from django import forms
from line_api.models import Member, System

class MemberEditForm(forms.ModelForm):
    # user_idは固定で表示
    user_id = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'input-border'})
    )
    
    # 名前と学年区分は選択肢
    name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'input-border'})
    )
    grade_class = forms.ChoiceField(
        choices=Member.GRADE_CHOICES,  
        required=True,
        widget=forms.Select(attrs={'class': 'input-border'})
    )

    class Meta:
        model = Member
        fields = ['user_id', 'name', 'grade_class']


class ScheduleEditForm(forms.ModelForm):

    schedule = forms.ChoiceField(choices=System.DAY_OF_WEEKS, required=True, widget=forms.Select(attrs={'class': 'input-border'}))
                               
    class Meta:
        model = System
        fields = ['schedule']

class ChiefEditForm(forms.ModelForm):

    chief = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'input-border'}))
                               
    class Meta:
        model = System
        fields = ['chief']

