from django import forms
from .models import Target


class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ('daily_target', 'weekly_target', 'monthly_target', 'yearly_target')
        
    def __init__(self, *args, **kwargs):
        super(TargetForm, self).__init__(*args, **kwargs)
        self.fields['daily_target'].widget.attrs.update({
            'class': 'form-control',
            'min': '1',
        })
        self.fields['weekly_target'].widget.attrs.update({
            'class': 'form-control',
            'min': '1',
        })
        self.fields['monthly_target'].widget.attrs.update({
            'class': 'form-control',
            'min': '1',
        })
        self.fields['yearly_target'].widget.attrs.update({
            'class': 'form-control',
            'min': '1',
        })
        
    def clean(self):
        cleaned_data = super().clean()
        daily = cleaned_data.get('daily_target', 0)
        weekly = cleaned_data.get('weekly_target', 0)
        monthly = cleaned_data.get('monthly_target', 0)
        yearly = cleaned_data.get('yearly_target', 0)
        
        # Ensure targets make sense (weekly > daily, monthly > weekly, etc.)
        if weekly < daily * 7:
            self.add_error('weekly_target', 'Weekly target should be at least 7 times daily target')
        
        if monthly < daily * 30:
            self.add_error('monthly_target', 'Monthly target should be at least 30 times daily target')
        
        if yearly < daily * 365:
            self.add_error('yearly_target', 'Yearly target should be at least 365 times daily target')
        
        return cleaned_data 