from django import forms

class RecommendationForm(forms.Form):
    gre_verbal = forms.FloatField(label='GRE Verbal', min_value=130, max_value=170)
    gre_quant = forms.FloatField(label='GRE Quantitative', min_value=130, max_value=170)
    gre_awa = forms.FloatField(label='GRE Analytical Writing', min_value=0, max_value=6)
    gpa = forms.FloatField(label='GPA', min_value=0, max_value=4)